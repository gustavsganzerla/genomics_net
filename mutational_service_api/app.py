from flask import Flask, request, jsonify
from decouple import config
import subprocess
import os
import uuid


def parse_snps_file(show_snps_file):
    snps = []
    with open(show_snps_file, 'r') as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith('=') or stripped.startswith('/') or stripped.startswith('NUCMER') or stripped.startswith('['):
                continue  #skip headers, comments, and empty lines
            fields = stripped.split()
            if len(fields) >= 8:
                snp = {
                    'pos_ref': fields[0],
                    'ref_base': fields[1],
                    'pos_query': fields[2],
                    'query_base': fields[3],
                    'ref_name': fields[-2],
                    'query_name': fields[-1]
                }
                snps.append(snp)
    return snps

app = Flask(__name__)

@app.route('/mutate', methods=['POST'])
def mutate():
    HOST_UPLOADS_DIR = os.getenv('HOST_UPLOADS_DIR', '/app/uploads')
    HOST_REFERENCES_DIR = os.getenv('HOST_REFERENCES_DIR', '/data/references')


    job_id = str(uuid.uuid4())
    
    data = request.get_json()
    filename = data.get('filename')
    reference_file = data.get('reference')

    ###input file
    file_path = os.path.join('/app/uploads', filename)
    
    ###create a directory for storing the output files
    outdir = f'/app/uploads/mutation_{job_id}'
    os.makedirs(outdir, exist_ok=True)

    ###reference file path
    reference_path = os.path.join('/data/references', reference_file)

    ###first, i will run a nucmer to generate a delta file
    nucmer_cmd = [
    'nucmer',
    '--prefix', f'mutation_{job_id}',
    reference_path,
    file_path
    ]
    try:
        result = subprocess.run(
            nucmer_cmd,
            cwd=outdir,  # run inside the output directory
            capture_output=True,  # capture stdout and stderr
            text=True,
            check=True
        )
        ###at this point, nucmer ran successfully and i should have a delta file
        ###i can now access it and convert the delta to vcf
        ###i will not install delta2vcf, instead i will parse the delta file manually

        delta_file = os.path.join(outdir, f'mutation_{job_id}.delta')
        if os.path.exists(delta_file):
            ###1. delta-filter from mummer
            delta_filter_file = os.path.join(outdir, f'mutation_{job_id}.delta_filter')
            with open (delta_filter_file, 'w') as df_outfile:
                subprocess.run(['delta-filter',
                                '-1',
                                delta_file],
                                stdout=df_outfile,
                                check=True
                                )
                ###lets ensure the delta-filter file exists and is not empty
                if os.path.exists(delta_filter_file) and os.path.getsize(delta_filter_file) > 0:
                    show_snps_file = os.path.join(outdir, f'mutation_{job_id}.snps')
                    with open(show_snps_file, 'w') as snps_outfile:
                        subprocess.run(['show-snps',
                                        '-Clr',
                                        delta_filter_file],
                                        stdout=snps_outfile,
                                        check=True
                                        )
                        
                        ###if the snps file was successfully created and is not empty
                        ###i will parse it and send to the django view (using json)

                        if os.path.exists(show_snps_file) and os.path.getsize(show_snps_file) > 0:
                            snps_list = parse_snps_file(show_snps_file)
                            return jsonify({
                                    'snps':snps_list,
                                    'message': 'success',
                                    'stderr': result.stderr,
                                    'snps_file':show_snps_file
                                })
            
    except subprocess.CalledProcessError as e:
        return jsonify({
            'message': 'error',
            'stderr': e.stderr
        }), 500
    





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
