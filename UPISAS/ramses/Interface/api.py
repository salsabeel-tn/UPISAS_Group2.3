


"""TODO: CHANGE THE PORTS FOR INSTANCE AND CONFIG MANAGER"""




from dataclasses import dataclass
from typing import Optional, Dict, List

from flask import Flask, Response, request

import requests
import os
import json

app = Flask(__name__)

monitor_schema_file = "specifications/monitor_schema.json"
adaption_option_file = "specifications/adaptation_options.json"
adaption_schema_file = "specifications/adaptation_schema.json"


@dataclass
class UnifiedRequest:
    operation: str  # "addInstances", "removeInstance", "changeLBWeights", or "changeProperty"
    serviceImplementationName: Optional[str] = None
    numberOfInstances: Optional[int] = None
    removeInstanceName: Optional[str] = None
    weightsId: Optional[str] = None
    weights: Optional[Dict[str, float]] = None
    instancesToRemoveWeightOf: Optional[List[str]] = None
    serviceName: Optional[str] = None
    propertiesName: Optional[str] = None
    propertiesToChange: Optional[str] = None
    address: Optional[str] = None
    port: Optional[int] = None


@app.route('/monitor', methods=['GET'])
def monitor():
    services = fetch_system_architecture()
    combined_data = {}
    if services:
        for service_name, details in services.items():
            service_id = details['serviceId']
            implementation_id = details['currentImplementationId']
            instances = details['instances']
            snapshot_config = fetch_service_snapshot(service_name)
            instance_config = fetch_instance_configuration(service_name, implementation_id)
            combined_data[service_name] = {
                'serviceId': service_id,
                'currentImplementationId': implementation_id,
                'instances': instances,
                'snapshot': snapshot_config,
                'instanceConfig': instance_config
            }
    return Response(
        response=json.dumps(combined_data),
        status=200,
        mimetype='application/json'
    )


@app.route('/monitor_schema', methods=['GET'])
def monitor_schema():
    try:
        data = get_schema(monitor_schema_file)
        return Response(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
    except FileNotFoundError as e:
        print(e)
        return Response(
            response=json.dumps({"error": "Schema file not found"}),
            status=404,
            mimetype='application/json'
        )


@app.route('/adaptation_options', methods=['GET'])
def adaptation_options():
    try:
        data = get_schema(adaption_option_file)
        return Response(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
    except FileNotFoundError as e:
        print(e)
        return Response(
            response=json.dumps({"error": "Schema file not found"}),
            status=404,
            mimetype='application/json'
        )


@app.route('/adaptation_options_schema', methods=['GET'])
def adaptation_options_schema():

    try:
        data = get_schema(adaption_schema_file)
        return Response(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
    except FileNotFoundError as e:
        print(e)
        return Response(
            response=json.dumps({"error": "Schema file not found"}),
            status=404,
            mimetype='application/json'
        )


@app.route('/execute', methods=['POST'])
def execute():
    try:
        data = request.get_json()
        req = UnifiedRequest(**data)

        if req.operation == "addInstances":
            if not req.serviceImplementationName or not req.numberOfInstances:
                return Response(
                    response=json.dumps({"error": "Missing required fields for addInstances"}),
                    status=400,
                    mimetype='application/json'
                )
            url = "http://localhost:32779/rest/addInstances"
            headers = {
                'Content-Type': 'application/json'
            }
            request_body = {
                "serviceImplementationName": req.serviceImplementationName,
                "numberOfInstances": req.numberOfInstances
            }
            response = requests.post(url, headers=headers, data=json.dumps(request_body)).json()

        elif req.operation == "changeLBWeights":
            if not req.weights:
                return Response(
                    response=json.dumps({"error": "Missing weights for changeLBWeights"}),
                    status=400,
                    mimetype='application/json'
                )
            url = "http://localhost:32780/rest/changeLBWeights"
            headers = {
                'Content-Type': 'application/json'
            }
            request_body = {
                "serviceID": req.weightsId,
                "newWeights": req.weights,
                "instancesToRemoveWeightOf": req.instancesToRemoveWeightOf
            }
            response = requests.post(url, headers=headers, data=json.dumps(request_body)).json()

        elif req.operation == "changeProperty":
            if not req.propertiesToChange:
                return Response(
                    response=json.dumps({"error": "Missing properties for changeProperty"}),
                    status=400,
                    mimetype='application/json'
                )
            URL = "http://localhost:32780/rest/changeProperty"
            headers = {
                'Content-Type': 'application/json'
            }
            request_body = {
                "serviceName": req.serviceName,
                "propertyName" : req.propertiesName,
                "value": req.propertiesToChange
            }
            response = {
                "message": "Properties updated successfully",
                "updatedProperties": req.propertiesToChange
            }

        elif req.operation == "removeInstance":

            if not req.serviceImplementationName or not req.address or req.port is None:
                return Response(
                    response=json.dumps({"error": "Missing required fields for removeInstance"}),
                    status=400,
                    mimetype='application/json'
                )
            url = "http://localhost:32779/rest/removeInstance"
            headers = {
                'Content-Type': 'application/json'
            }
            request_body = {
                "serviceImplementationName": req.serviceImplementationName,
                "address": req.address,
                "port": req.port
            }

            response = requests.post(url, headers=headers, data=json.dumps(request_body)).json()

        else:
            return Response(
                response=json.dumps({"error": "Invalid operation"}),
                status=400,
                mimetype='application/json'
            )

        return Response(
            response=json.dumps(response),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        return Response(
            response=json.dumps({"error": str(e)}),
            status=500,
            mimetype='application/json'
        )


@app.route('/execute_schema', methods=['GET'])
def execute_schema():
    try:
        data = get_schema(adaption_schema_file)
        return Response(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
    except FileNotFoundError as e:
        print(e)
        return Response(
            response=json.dumps({"error": "Schema file not found"}),
            status=404,
            mimetype='application/json'
        )


def fetch_system_architecture():
    #probe
    url = "http://localhost:32838/rest/systemArchitecture"

    try:
        response = requests.get(url)
        response.raise_for_status()
        print("data fetched")
        architecture_data = response.json()
        return architecture_data
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def fetch_instance_configuration(serviceName, implementationId):
    #probe
    url = "http://localhost:32838/rest/service/{}/configuration?implementationId={}".format(serviceName,
                                                                                            implementationId)
    try:
        response = requests.get(url)
        response.raise_for_status()
        print("instance configuration data fetched")
        instance_configuration = response.json()
        return instance_configuration
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def fetch_service_snapshot(serviceName):
    #probe
    url = "http://localhost:32838/rest/service/{}/snapshot".format(serviceName)
    try:
        response = requests.get(url)
        response.raise_for_status()
        print("snapshot data fetched")
        snapshot_data = response.json()
        return snapshot_data
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def get_schema(file):
    try:
        with open(file, "r") as schema_file:
            schema = json.load(schema_file)
            return schema
    except FileNotFoundError as e:
        print(e)
        return None


if __name__ == '__main__':
    print("RAMES APIs available at http://127.0.0.1:500000/")
    app.run(debug=True, port=500000)
