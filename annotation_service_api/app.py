from flask import Flask, request, jsonify
import os
import tempfile
import subprocess
import uuid


app = Flask(__name__)

@app.route('/annotate', methods=['POST'])
def annotate():
    ###the absolute path of the file was sent here, the flask app should have access to it
    data = request.get_json(force=True)
    

    if not data or 'filename' not in data:
        return jsonify({'error': 'Missing file_path in request.'}), 400

    filename = data['filename']
    reference_file = data.get('reference')
    file_path = f"/app/uploads/{filename}"

    if not os.path.isfile(file_path):
        return jsonify({'error': f"File not found: {file_path}"}), 400

    job_id = str(uuid.uuid4())
    output_dir = f"/app/uploads/output_{job_id}"

    prokka_cmd = [
        'docker', 'run', '--rm',
        '--platform', 'linux/amd64',
        '-v', '/Users/gustavosganzerla/Documents/mpox_outbreak/genomics_net/annotation_service_api/uploads:/data',
        '-v', '/Users/gustavosganzerla/Documents/mpox_outbreak/genomics_net/references:/data/references',
        'staphb/prokka:latest',
        'prokka',
        '--outdir', f'/data/output_{job_id}',
        '--prefix', 'annotated_genome',
        '--proteins', '/data/references/{reference_file}',
        f'/data/{filename}'
    ]

    try:
        result = subprocess.run(
            prokka_cmd, capture_output=True, text=True, check=True
        )
        print("Prokka stdout:", result.stdout, flush=True)
        print("Prokka stderr:", result.stderr, flush=True)

    except subprocess.CalledProcessError as e:
        print("Prokka failed:", e.stderr, flush=True)
        return jsonify({'error': 'Prokka annotation failed', 'details': e.stderr}), 500

    return jsonify({
        'message': f'Prokka annotation completed for {filename}.',
        'job_id': job_id
    })

    
    






#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
    
#     genome_file = request.files['file']
#     if genome_file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     # Create a temp directory and save file there
#     temp_dir = "/app/uploads"
#     os.makedirs(temp_dir, exist_ok=True)
#     file_path = os.path.join(temp_dir, genome_file.filename)
#     genome_file.save(file_path)

#     host_upload_dir = "/Users/gustavosganzerla/Documents/mpox_outbreak/genomics_net/annotation_service_api/uploads"

    
#     job_id = str(uuid.uuid4())
#     output_dir = f"/data/output_{job_id}"

#     prokka_cmd = [
#     'docker', 'run', '--rm',
#     '--platform', 'linux/amd64',   # for M1 Macs
#     '-v', '/Users/gustavosganzerla/Documents/mpox_outbreak/genomics_net/annotation_service_api/uploads:/data',
#     '-v', '/Users/gustavosganzerla/Documents/mpox_outbreak/genomics_net/references:/data/references',
#     'staphb/prokka:latest',
#     'prokka',
#     '--outdir', f'/data/output_{job_id}',
#     '--prefix', 'annotated_genome',
#     '--proteins', '/data/references/NC_003310.faa',
#     f'/data/{genome_file.filename}'
# ]

#     file_path = os.path.join(temp_dir, genome_file.filename)

#     try:
#         result = subprocess.run(
#             prokka_cmd, capture_output=True, text=True, check=True
#         )
#         #print("Prokka stdout:", result.stdout, flush=True)
#         #print("Prokka stderr:", result.stderr, flush=True)
#     except subprocess.CalledProcessError as e:
#         print("Prokka failed:", e.stderr, flush=True)
#         return jsonify({'error': 'Prokka annotation failed', 'details': e.stderr}), 500

#     return jsonify({'message': f'Prokka annotation completed for {genome_file.filename}.',
#                     'job_id':job_id})





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
