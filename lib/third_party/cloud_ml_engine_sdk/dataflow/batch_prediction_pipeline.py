# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Dataflow pipeline for batch prediction in Cloud ML."""
import json
import os
import apache_beam as beam
from apache_beam.io.textio import WriteToText
import batch_prediction
from google.cloud.ml.dataflow.io.multifiles_source import ReadFromMultiFilesText
from google.cloud.ml.dataflow.io.multifiles_source import ReadFromMultiFilesTFRecord
from google.cloud.ml.dataflow.io.multifiles_source import ReadFromMultiFilesTFRecordGZip

OUTPUT_RESULTS_FILES_BASENAME_ = "prediction.results"


OUTPUT_ERRORS_FILES_BASENAME_ = "prediction.errors_stats"


def run(p, args, aggregator_dict, cloud_logger=None):
  """Run the pipeline with the args and dataflow pipeline option."""
  # Create a PCollection for model directory.
  model_dir = p | "Create Model Directory" >> beam.Create([args.model_dir])

  input_file_format = args.input_file_format.lower()

  # Setup reader.
  if input_file_format == "text":
    reader = p | "READ_TEXT_FILES" >> ReadFromMultiFilesText(
        args.input_file_patterns)
  elif input_file_format == "tfrecord":
    reader = p | "READ_TF_FILES" >> ReadFromMultiFilesTFRecord(
        args.input_file_patterns)
  elif input_file_format == "tfrecord_gzip":
    reader = p | "READ_TFGZIP_FILES" >> ReadFromMultiFilesTFRecordGZip(
        args.input_file_patterns)

  # Setup the whole pipeline.
  results, errors = (reader
                     | "BATCH_PREDICTION" >> batch_prediction.BatchPredict(
                         beam.pvalue.AsSingleton(model_dir),
                         batch_size=args.batch_size,
                         aggregator_dict=aggregator_dict,
                         cloud_logger=cloud_logger))

  # Convert predictions to JSON and then write to output files.
  _ = (results
       | "TO_JSON" >> beam.Map(json.dumps)
       | "WRITE_PREDICTION_RESULTS" >> WriteToText(
           os.path.join(args.output_location, OUTPUT_RESULTS_FILES_BASENAME_)))
  # Write prediction errors counts to output files.
  _ = (errors
       | "GROUP_BY_ERROR_TYPE" >> beam.combiners.Count.PerKey()
       | "WRITE_ERRORS" >> WriteToText(
           os.path.join(args.output_location, OUTPUT_ERRORS_FILES_BASENAME_)))

  return p.run()
