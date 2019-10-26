add_to_zip () {
    cp dependencies.zip $1.zip && zip -g $1.zip $1_lambda.py
}

upload_to_s3 () {
    aws s3 cp $1.zip s3://$BUCKET/lambda/src/$1.zip
}

update_lambda_function () {
    aws lambda update-function-code \
    --function-name $1 \
    --s3-bucket $BUCKET \
    --s3-key lambda/src/$2.zip
}

echo "📁 Moving /lambdas/ folder contents to root dependencies folder 📁"
mv ./lambdas/* .
rmdir ./lambdas

echo "🤐 Zipping up initial dependencies 🤐"
cd ./dependencies && zip -r dependencies.zip .
cd ..

echo "📁 Moving dependencies.zip file to root project directory 📁"
mv ./dependencies/dependencies.zip .

api_handler="api_handler coffeepot-dev-api-handler"

for i in "$api_handler"
do
    set -- $i
    zip_file_name=$1
    lambda_function_name=$2

    echo "📦 Packaging files for $lambda_function_name lambda 📦"
    add_to_zip $zip_file_name
    echo "📁 Uploading $zip_file_name.zip file to S3 for $lambda_function_name lambda 📁"
    upload_to_s3 $zip_file_name
    echo "🆕 Updating $lambda_function_name lambda 🆕"
    update_lambda_function $lambda_function_name $zip_file_name
done