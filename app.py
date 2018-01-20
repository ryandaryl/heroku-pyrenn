import os
from flask import Flask, request, jsonify, render_template
from rq import Queue
from worker import conn
from worker_tasks import run_script

app = Flask(__name__)
q = Queue(connection=conn)

def get_status(job):
    status = {
        'id': job.id,
        'result': job.result,
        'status': 'failed' if job.is_failed else 'pending' if job.result == None else 'completed'
    }
    status.update(job.meta)
    return jsonify(status)

@app.route("/")
def handle_job():
    query_id = request.args.get('job')
    if query_id:
        found_job = q.fetch_job(query_id)
        if found_job:
            output = render_template('output.html', output=found_job.result) if found_job.result else get_status(found_job)
        else:
            output = { 'id': None, 'error_message': 'No job exists with the id number ' + query_id }
    else:
        new_job = q.enqueue(run_script, 'scripts/example_friction.py', timeout='1h')
        output = get_status(new_job)
    return output

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)