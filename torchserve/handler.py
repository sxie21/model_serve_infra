from ts.torch_handler.base_handler import BaseHandler
from ts.metrics.metric_type_enum import MetricTypes
import torch
import json
from model import SimpleModel
#from prometheus_client import Gauge


class SimpleHandler(BaseHandler):
    def __init__(self):
        super(SimpleHandler, self).__init__()
        self.model = SimpleModel()
    
    def initialize(self, context):
         
        metrics = context.metrics
        self.model.load_state_dict(torch.load("model.pth", map_location=torch.device('cpu')))
        self.model.eval()

        # metrics
        self.inf_request_count = metrics.add_metric_to_cache(
            metric_name="inference_request_count",
            unit="count",
            dimension_names=[],
            metric_type=MetricTypes.COUNTER,
        )

        self.mean_metric = metrics.add_metric_to_cache(
            metric_name="input_mean_x1", 
            unit="value", 
            dimension_names=[], 
            metric_type=MetricTypes.GAUGE 
        )
        
        self.var_metric = metrics.add_metric_to_cache(
            metric_name="input_variance_x1", 
            unit="value", 
            dimension_names=[], 
            metric_type=MetricTypes.GAUGE
        )

        self.mean_metric = metrics.add_metric_to_cache(
            metric_name="input_mean_x2", 
            unit="value", 
            dimension_names=[], 
            metric_type=MetricTypes.GAUGE 
        )
        
        self.var_metric = metrics.add_metric_to_cache(
            metric_name="input_variance_x2", 
            unit="value", 
            dimension_names=[], 
            metric_type=MetricTypes.GAUGE
        )        





    def preprocess(self, data):

        #data processing
        preprocessed_data = data[0].get("data",None)
        if preprocessed_data is None:
            preprocessed_data = data[0]['body']['data']


        if len(preprocessed_data) != 2: #hard code TODO
            raise ValueError("Invalid Input, please make sure input data length is 2")  
        preprocessed_data = torch.tensor(preprocessed_data).float()
        return preprocessed_data

    def inference(self, input_tensor):
        
        with torch.no_grad():
            output = self.model(input_tensor)
        
        self.inf_request_count.add_or_update(value=1, dimension_values=[])

        # inference_count_metric = metrics.get_metric(
        #     metric_name="InferenceRequestCount", metric_type=MetricTypes.COUNTER
        # )
        # inference_count_metric.add_or_update(
        #     value=1, dimension_values=[self.context.model_name]
        # )        

        return output

    def postprocess(self, inference_output):
        
        
        postprocess_output = [{"output": inference_output.item()}]
    
        return postprocess_output

    def handle(self, data, context):
        """
        Invoke by TorchServe for prediction request.
        Do pre-processing of data, prediction using model and postprocessing of prediciton output
        :param data: Input data for prediction
        :param context: Initial context contains model server system properties.
        :return: prediction output
        """
        
        model_input = self.preprocess(data)
        model_output = self.inference(model_input)
        return self.postprocess(model_output)
    

    # def _update_incremental_stats(self, preprocessed_data):

    #     """
    #     calculate incremental mean and variance
    #     """
    #     x1, x2 = preprocessed_data

    #     self.x1_count += 1
    #     self.x2_count += 1

    #     x1_delta = x1 - self.x1_mean
    #     x2_delta = x2 - self.x2_mean

    #     self.x1_mean += x1_delta / (self.x1_count)
    #     self.x2_mean += x2_delta / (self.x2_count)
        
    #     self.x1_variance += x1_delta * (x1 - self.x1_mean)
    #     self.x2_variance += x2_delta * (x2 - self.x1_mean)

    
        #self._update_prometheus_metrics(stat_name)

    # def _update_prometheus_metrics(self, stat_name):
    #         """
    #         update prometheus metrics
    #         """
    #         if stat_name == 'x1':
    #             self.x1_distribution.labels(stat='mean').set(self.x1_mean)
    #             self.x1_distribution.labels(stat='std').set((self.x1_variance / self.x1_count)**0.5)
    #         elif stat_name == 'x2':
    #             self.x2_distribution.labels(stat='mean').set(self.x2_mean)
    #             self.x2_distribution.labels(stat='std').set((self.x2_variance / self.x2_count)**0.5)        