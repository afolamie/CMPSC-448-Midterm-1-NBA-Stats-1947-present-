import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

def make_text(df, mode):
    if mode == "prompt":
        return df.LLM_Input.astype(str).tolist()
    if mode == "response":
        return df.LLM_output.astype(str).tolist()
    if mode == "combined":
        return (df.LLM_Input.astype(str)+" [SEP] "+df.LLM_output.astype(str)).tolist()
    raise ValueError(mode)

def validate_splits(train, val, test):
    required = {"LLM_name", "LLM_Input", "LLM_output"}
    groups = []
    for df in (train, val, test):
        if df.empty or not required.issubset(df.columns):
            raise ValueError("Missing required columns or empty split")
        groups.append(set(df.LLM_Input.astype(str)))
    if groups[0]&groups[1] or groups[0]&groups[2] or groups[1]&groups[2]:
        raise ValueError("Prompt leakage between splits")
    if not set(val.LLM_name).union(test.LLM_name).issubset(set(train.LLM_name)):
        raise ValueError("Unknown label in held-out split")

def evaluate(kind, mode, train, val, test, epochs, seed, out):
    import tensorflow as tf
    tf.keras.utils.set_random_seed(seed)
    enc = LabelEncoder().fit(train.LLM_name)
    ys = [enc.transform(df.LLM_name) for df in (train,val,test)]
    xs = [np.array(make_text(df,mode)) for df in (train,val,test)]
    vectorize = tf.keras.layers.TextVectorization(max_tokens=20000,output_mode="int",output_sequence_length=300)
    vectorize.adapt(tf.data.Dataset.from_tensor_slices(xs[0]).batch(64))
    inp = tf.keras.Input(shape=(),dtype=tf.string)
    x = tf.keras.layers.Embedding(20000,96)(vectorize(inp))
    if kind == "cnn":
        x = tf.keras.layers.GlobalMaxPooling1D()(tf.keras.layers.Conv1D(96,5,activation="relu")(x))
    else:
        x = tf.keras.layers.LSTM(64)(x)
    x = tf.keras.layers.Dropout(.35)(x)
    model = tf.keras.Model(inp,tf.keras.layers.Dense(len(enc.classes_),activation="softmax")(x))
    model.compile(optimizer="adam",loss="sparse_categorical_crossentropy",metrics=["accuracy"])
    model.fit(xs[0],ys[0],validation_data=(xs[1],ys[1]),epochs=epochs,batch_size=32,verbose=2,
              callbacks=[tf.keras.callbacks.EarlyStopping(patience=3,restore_best_weights=True,monitor="val_loss")])
    pred = model.predict(xs[2],verbose=0).argmax(axis=1)
    result = {"model":kind,"mode":mode,"accuracy":float(accuracy_score(ys[2],pred)),
              "macro_f1":float(f1_score(ys[2],pred,average="macro",zero_division=0)),
              "classes":enc.classes_.tolist(),
              "confusion_matrix":confusion_matrix(ys[2],pred,labels=range(len(enc.classes_))).tolist(),
              "report":classification_report(ys[2],pred,labels=range(len(enc.classes_)),
                                             target_names=enc.classes_,output_dict=True,zero_division=0)}
    out.mkdir(parents=True,exist_ok=True)
    (out/f"{kind}_{mode}_metrics.json").write_text(json.dumps(result,indent=2))
    pd.DataFrame({"truth":enc.inverse_transform(ys[2]),"prediction":enc.inverse_transform(pred)}).to_csv(
        out/f"{kind}_{mode}_predictions.csv",index=False)
    tf.keras.backend.clear_session()
    return result

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--data-dir",default="data/splits")
    p.add_argument("--output",default="results")
    p.add_argument("--epochs",type=int,default=12)
    p.add_argument("--seed",type=int,default=448)
    a=p.parse_args()
    d=Path(a.data_dir)
    datasets=[pd.read_csv(d/f"{name}.csv").fillna("") for name in ("train","validation","test")]
    validate_splits(*datasets)
    out=Path(a.output)
    results=[evaluate(k,m,*datasets,a.epochs,a.seed,out) for m in ("prompt","response","combined") for k in ("cnn","lstm")]
    pd.DataFrame([{q:r[q] for q in ("model","mode","accuracy","macro_f1")} for r in results]).to_csv(
        out/"comparison.csv",index=False)
