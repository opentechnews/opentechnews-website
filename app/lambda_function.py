import feedparser
from feedparser import parse
import os
import boto3 # AWS Client
import logging
from urllib.parse import urlparse, parse_qs

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Feed URL: "Open source technology"
feed_url = "https://www.google.com/alerts/feeds/07480943305324684294/8607219941662562161"


s3 = boto3.client('s3')

def fetch_feed(url):
    logger.info("Fetching Feed...")
    return feedparser.parse(url)

# Process articles and return HTML content
def process_articles(feed):
    logger.info("Processing articles...")
    html_content = '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Open Tech News</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="styles/main.css" rel="stylesheet">
</head>
<body>
    <!-- Floating button --> 
    <script src="https://static.elfsight.com/platform/platform.js" data-use-service-core defer></script>
    <div class="elfsight-app-2f74152d-a39e-4841-bc40-d968690b9dea" data-elfsight-app-lazy></div>

    <div class="container">
        
    <div class="container container-custom">
        <h1 class="bottom-left">Open Tech News</h1>
        <a href="https://store.opentech.news/" class="bottom-right">Store</a>
    </div>
        

    <div class="list-group">
    
    '''
    
    if feed.entries:
        logger.info("Found articles.")
    else:
        logger.info("Did not find articles")

    for article in feed.entries:

        # Extract the 'url=' parameter from the article link
        parsed_url = urlparse(article.link)
        query_params = parse_qs(parsed_url.query)
        article_url = query_params.get('url', [''])[0]
        
        html_content += f'''
        <a href="{article_url}" class="list-group-item list-group-item-action">{article.title}</a>\n
        '''
    
    # Footer
    html_content += '''
    </div> <!-- /list-group -->
    </div> <!-- /container -->



    <!-- Bootstrap Style Code -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>

    </body>
    </html>'''
    return html_content

def save_to_s3(html_content, bucket_name, file_name):
    s3.put_object(
        Body=html_content, 
        Bucket=bucket_name, 
        Key=file_name,
        ContentType='text/html') # Important


if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
    # When run in AWS Lambda
    def lambda_handler(event, context):
        feed = fetch_feed(feed_url)
        html_content = process_articles(feed)
        bucket_name = 'opentech.news-public'
        file_name = 'index.html'
        logger.info("Saving to S3...")
        save_to_s3(html_content, bucket_name, file_name)
else:
    # Code run locally
    feed = fetch_feed(feed_url)
    html_content = process_articles(feed)
    file_name = '_PUBLIC/index.html'
    with open(file_name, 'w') as f:
        f.write(html_content)
    logger.info(f"HTML file saved locally as {file_name}")

    # Upload to AWS
    bucket_name = 'opentech.news-public'
    file_name = 'index.html'
    logger.info("Saving to S3...")
    save_to_s3(html_content, bucket_name, file_name)