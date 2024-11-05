import torch
from fastapi import FastAPI
from pydantic import BaseModel
import torch.nn as nn
from typing import List
from model import SimpleModel



app = FastAPI()

class InputData(BaseModel):
    input: List[float]  


class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc = nn.Linear(2, 1)  

    def forward(self, x):
        return self.fc(x)


app = FastAPI()


model = SimpleModel()  
model.load_state_dict(torch.load("model.pth"))  
model.eval()  


def predict(input_data: List[float]):
    input_tensor = torch.tensor(input_data).float()
    input_tensor = input_tensor.unsqueeze(0)  

    with torch.no_grad():
        output = model(input_tensor)
    return output.item() 

@app.post("/predict")
async def predict_endpoint(data: InputData):
    prediction = predict(data.input)
    return {"prediction": prediction}