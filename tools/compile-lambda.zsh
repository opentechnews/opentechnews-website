# Description:
# - Copies python file to /release
# - Packages python dependencies into /release
# - Creates zip file for uploading to AWS


cp app/lambda_function.py app/release/
cd app/release
pip install feedparser --target .
zip lambda.zip -r ./*