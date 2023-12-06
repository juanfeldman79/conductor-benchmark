import uuid
import time

import threading
import requests

# constants
CONDUCTOR_API = 'http://localhost:8080/api'
WF_NAME = 'example_python_jfeldman_4RYG'
MAX_EXECUTIONS = 500
POOLING_SEC = 1
PAYLOAD = {
    "application": "example",
    "docType": "attachment",
    "docVersion": "1.0",
    "docID": "678",
    "docOP": "create",
    "docArgs": {
        "docSource": "s3://ai-team/recsys/rapps/example/678.json"
    },
    "parameters": {
        "ocrCacheEnabled": True
    }
}


def run_workflow(cid: str):
    print(f"Running workflow with correlation id: {cid}")
    payload = dict(PAYLOAD)
    payload["docID"] = time.time_ns()
    r = requests.post(f"{CONDUCTOR_API}/workflow/{WF_NAME}?correlationId={cid}", json=payload)
    print(f"Workflow id: ", r.text)


if __name__ == "__main__":
    start_time = time.time()

    # run workflows
    for i in range(0, MAX_EXECUTIONS):
        print("Execution: ", i)

        # create correlation id
        correlation_id = str(uuid.uuid4())

        # run workflow
        threading.Thread(target=run_workflow, args=(correlation_id,)).start()

    # wait for Conductor
    time.sleep(2)

    # wait to finish
    wait = True
    while wait:
        # query Conductor
        resp = requests.get(
            f'{CONDUCTOR_API}/workflow/search?query=status="RUNNING" AND workflowType="{WF_NAME}"',
            json=PAYLOAD)
        # resp = requests.get(
        #     f'{CONDUCTOR_API}/workflow/running/{WF_NAME}',
        #     json={})

        # check response
        total_hits = resp.json()['totalHits']
        # total_hits = len(resp.json())
        wait = total_hits != 0
        print(f"Waiting for {total_hits} executions...")

        # sleep
        if wait:
            time.sleep(POOLING_SEC)

    # finish
    total_time = time.time() - start_time
    print(f"Total time {total_time} seconds")
