from django.shortcuts import render
from django.http import HttpResponse, FileResponse, HttpResponseNotFound
from zipfile import ZipFile
from . forms import GenomeForm
import requests
import json
import logging
import os
import uuid
from Bio import SeqIO
from io import StringIO, BytesIO

logger = logging.getLogger(__name__)

# Create your views here.
def home(request):
    return render(request, 'frontend/home.html')

def upload_genome(request):
    if request.method == 'POST':
        form = GenomeForm(request.POST, request.FILES)
        if form.is_valid():
            collected_data = form.cleaned_data
            uploaded_file = collected_data.get('uploaded_file')


            length = 0
            header = ''
            if uploaded_file:

                ###the file only exists in memory
                uploaded_file_data = uploaded_file.read().decode('utf-8')
                uploaded_file_io = StringIO(uploaded_file_data)

                ###basic statistics on the uploaded genome
                for record in SeqIO.parse(uploaded_file_io, 'fasta'):
                    length = len(record.seq)
                    header = record.id
                    a_proportion = (record.seq.count('A')/length)*100
                    t_proportion = (record.seq.count('T')/length)*100
                    c_proportion = (record.seq.count('C')/length)*100
                    g_proportion = (record.seq.count('G')/length)*100
                    n_proportion = (record.seq.count('N')/length)*100

                ###now i need to write the file persistently to disk
                job_id = str(uuid.uuid4())
                filename = f"{job_id}.fasta"
                file_path = os.path.join('/app/uploads', filename)

                ###the file is now uploaded into /app/uploads, which is a pointer to /Users/gustavosganzerla/Documents/mpox_outbreak/genomics_net/annotation_service_api/uploads
                with open(file_path, 'w') as out_file:
                    out_file.write(uploaded_file_data)

                    

                

           
            return render(request, 'frontend/result_upload.html', {'header':header,
                                                            'length':length,
                                                            'a_proportion':f"{a_proportion:.2f}",
                                                            't_proportion':f"{t_proportion:.2f}",
                                                            'c_proportion':f"{c_proportion:.2f}",
                                                            'g_proportion':f"{g_proportion:.2f}",
                                                            'n_proportion':f"{n_proportion:.2f}",
                                                            'filename':filename})
    else:
        form = GenomeForm()
    return render(request, 'frontend/upload.html', {'form': form})


def annotate_genome(request, filename):
    
    selected_reference = request.GET.get('reference')

    payload = {'filename':filename,
               'reference':selected_reference}
    
    try:
        response = requests.post('http://annotation_service_api:5000/annotate',
                                json=payload)
        response.raise_for_status()
        result = response.json()
        
        ###now I should've got a response back from the api
        job_id = result.get('job_id')
        uploads_dir = '/app/uploads'
        job_folder = f"output_{job_id}"

        full_path = os.path.join(uploads_dir, job_folder)

        files = os.listdir(full_path)
        

    except requests.RequestException as e:
        logger.error(f'Annotation service error: {e}')
        return HttpResponse(e)
    
    return render(request, 'frontend/annotation_results.html', {'files':files,
                                                                'job_id':job_id,
                                                                'selected_reference':selected_reference})

def download_annotation(request, job_id):
    ###a post is comming from the template
    if request.method == 'POST':
        selected_files = request.POST.getlist('selected_files')
        if not selected_files:
            return HttpResponse('No files selected')
        
        uploads_dir = '/app/uploads'
        job_folder = f'output_{job_id}'

        full_path = os.path.join(uploads_dir, job_folder)

        ###if it's one file only, download directly
        if len(selected_files)==1:
            file_path = os.path.join(full_path, selected_files[0])
            if os.path.exists(file_path):
                return FileResponse(open(file_path, 'rb'), as_attachment=True)
            else:
                return HttpResponseNotFound('File not found')
            
        ###for multiple files, I have to zip them
        else:
            zip_buffer = BytesIO()

            with ZipFile(zip_buffer, 'w') as zip_file:
                for filename in selected_files:
                    file_path = os.path.join(full_path, filename)
                    if os.path.exists(file_path):
                        zip_file.write(file_path, arcname=filename)
            
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="annotation_files.zip"'
            return response

        
    
