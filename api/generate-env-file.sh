ENV_FILE="/home/ec2-user/ais/.env"
echo "" > $ENV_FILE

write_param() {
  echo "$1=$2" >> $ENV_FILE
}

load_params() {
  local prefix=$1
  local params
  params=$(aws ssm get-parameters-by-path \
    --path "$prefix" \
    --with-decryption \
    --region us-east-2 \
    --query "Parameters[*].[Name,Value]" \
    --output text)

  while read -r name value; do
    key=$(basename "$name")
    export "$key=$value"
    write_param "$key" "$value"
  done <<< "$params"
}

load_params "/ais-ws-broadcaster/"
load_params "/ais-repository/"
load_params "/ais-ingestor/"

echo "Generated .env file:"
cat $ENV_FILE
