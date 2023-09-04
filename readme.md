# DynamoDb Data Clone

## A Cli tool to clone Data between 2 DynamoDbTables in pyhton

This CLI tool copy data between 2 DynamoDb Tables with the same key definition, the tables can be in different AWS accounts or regions.

The source and destiny accounts is determined by the AWS CLI profiles configured

The source and destiny tables are set ina interacte way before the data copy start.

The copy process is done through AWS Python SDK (boto3) using the `scan` operation and write using `batch_write_item` operation in 25 items block

### Pre-requisites

- Python installed
- AWS CLI Installed
- At least one AWS configured profile (See https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html#cli-configure-files-using-profiles) with read and write permissions to the source and destination table
- A couple of DynamoDB tables wuth the same key definition

### Instalation

1. Clone repository

   ```
   git clone https://github.com/nelsonmora48/dynamodbclone
   ```

2. Move to cloned folder
   ```
   cd dynamodbclone
   ```
3. [Optional] Install and use virtualenv (recommended)

   ```
   pyhton -m venv .venv
   source .venv/bin/activate
   ```

4. Installing dependencies
   ```
   pip install -r requirements.txt
   ```

### Usage

`python main.py`

The interactive CLI guide you to select the source and destinatn profiles and tables,
