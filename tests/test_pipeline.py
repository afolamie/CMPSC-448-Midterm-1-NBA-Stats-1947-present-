import unittest
import pandas as pd
from prepare_test_data import prepare
from evaluate_models import validate_splits, make_text

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame([
            {"LLM_name":name,"LLM_Input":f"Prompt {i}","LLM_output":f"{name} says {i}"}
            for i in range(30) for name in ("gpt","claude","gemini")
        ])
    def test_no_leakage(self):
        validate_splits(*prepare(self.data))
    def test_reproducible(self):
        a,b=prepare(self.data),prepare(self.data)
        self.assertEqual([d.to_csv(index=False) for d in a],[d.to_csv(index=False) for d in b])
    def test_leakage_detected(self):
        train,val,test=prepare(self.data)
        val.loc[val.index[0],"LLM_Input"]=train.iloc[0].LLM_Input
        with self.assertRaises(ValueError):
            validate_splits(train,val,test)
    def test_missing_column(self):
        with self.assertRaises(ValueError):
            prepare(self.data.drop(columns="LLM_output"))
    def test_text_modes(self):
        self.assertEqual(make_text(self.data.iloc[:1],"prompt"),["Prompt 0"])
        self.assertIn("[SEP]",make_text(self.data.iloc[:1],"combined")[0])

if __name__=="__main__":
    unittest.main()
