"""
python aws/aws_glue/glue_job_params.py
"""

import sys
import boto3
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext

# Get only the JOB_NAME passed
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
job_name = args['JOB_NAME']

# Fetch job parameters using boto3
def get_glue_job_arguments(job_name):
    glue_client = boto3.client('glue')
    response = glue_client.get_job(JobName=job_name)
    
    # DefaultArguments looks like: {'--input_path': '...', '--output_path': '...'}
    default_args = response['Job']['DefaultArguments']
    
    # Strip off the "--" prefix
    parsed_args = {k.lstrip('--'): v for k, v in default_args.items() if k.startswith('--')}
    return parsed_args

# Inject fetched args
job_args = get_glue_job_arguments(job_name)

# For convenience, merge with JOB_NAME to maintain Glue job setup
job_args['JOB_NAME'] = job_name

# Initialize Spark/Glue
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(job_name, job_args)

# ✅ Use parameters now
input_path = job_args.get('input_path')
output_path = job_args.get('output_path')

print(f"Reading from: {input_path}")
print(f"Writing to: {output_path}")

# Sample read/write
df = spark.read.option("header", "true").csv(input_path)
df.show()

df.write.mode("overwrite").json(output_path)

job.commit()
