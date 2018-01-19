# Copyright (c) General Electric Company, 2017.  All rights reserved.

# Rt 106

# Whole-Cell-Segmentation algorithm adaptor

import os, glob, uuid, time, logging, subprocess

# function: run_algorithm() -- Python function for marshalling your data and running your algorithm.
# parameters:
#   datastore: object to be used when interacting with the Rt. 106 datastore
#   context:  A JSON structure that should contain all the inputs and parameters your algorithm needs.
def run_algorithm(datastore,context):

    logging.info('run_algorithm: %r' % context)

    # cleanup the input and output directories
    for f in glob.glob('/rt106/input/*') + glob.glob('/rt106/output/*'):
        os.remove(f)

    # 1. Code for marshalling inputs.
    input_path1 = datastore.get_pathology_primary_path(context['slide'], context['region'], 'DAPI')
    input_image1 = 'DAPI.tif'
    datastore.get_instance(input_path1,'/rt106/input', input_image1, 'tiff16')
    
    if 'channel' in context:
        input_path2 = datastore.get_pathology_primary_path(context['slide'], context['region'], context['channel'])
        logging.info('input_path2 %s' % input_path2)
        input_image2 = 'Cell.tif'
        input_file2 = '/rt106/input/%s' % input_image2
        datastore.get_instance(input_path2,'/rt106/input', input_image2, 'tiff16')
   
    output_path1 = datastore.get_pathology_result_path(context['slide'], context['region'], context['branch'], 'NucSeg')
    output_image1 = 'NucSeg.tif'
    output_file1 = '/rt106/output/%s' % output_image1
    
    output_path2 = datastore.get_pathology_result_path(context['slide'], context['region'], context['branch'], 'CellSeg') 
    output_image2 = 'CellSeg.tif'
    output_file2 = '/rt106/output/%s' % output_image2
    
    # 2.    Code for calling algorithm.
    try:
        input_args = '/rt106/input/DAPI.tif ' + output_file1 + " " +  output_file2 + " " + str(context['minLevel']) + " " + str(context['maxLevel']) + " " + str(context['smoothingSigma']) + " " + str(context['maxCytoplasmThickness'])
        if 'channel' in context:
            input_args = input_args + " " + input_file2 + " " + str(context['cellSegSensitivity'])
       
        logging.info('input_args %s' % input_args)
        run_algorithm = '/usr/bin/python WholeCellSeg.py %s' % (input_args)
        logging.info('run Algorithm: %r' % run_algorithm)
        subprocess.check_call(run_algorithm,shell=True)
    except subprocess.CalledProcessError, e:
        logging.error('%d - %s' % (e.returncode, e.cmd))
        status = "EXECUTION_FINISHED_ERROR"
        result_context = {}
        return { 'result' : result_context, 'status' : status }

    # 3.    Set status.
    status = "EXECUTION_FINISHED_SUCCESS"

    # 4.    Store results in datastore.

    response_upload1 = datastore.post_instance(output_path1,  '/rt106/output', output_image1,  'tiff16', context['force'])
    response_upload2 = datastore.post_instance(output_path2,  '/rt106/output', output_image2,  'tiff16', context['force'])
    
    if response_upload1 == 403 or response_upload2 == 403:
        status = "EXECUTION_ERROR"
               
    # 5.    Create JSON structure containing results.
    result_context = {
        "nucleiImage" : input_path1,
        "nucleiMap" : response_upload1['path'],
        "cellMap" : response_upload2['path']
    }

    return { 'result' : result_context, 'status' : status }
