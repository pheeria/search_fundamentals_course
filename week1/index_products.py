# From https://github.com/dshvadskiy/search_with_machine_learning_course/blob/main/index_products.py
from lxml import etree

import click
import glob
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
import logging

from time import perf_counter
import concurrent.futures



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')

# NOTE: this is not a complete list of fields.  If you wish to add more, put in the appropriate XPath expression.
# TODO: is there a way to do this using XPath/XSL Functions so that we don't have to maintain a big list?
mappings = {
    "sku/text()": "sku", # SKU is the unique ID, productIds can have multiple skus
    "productId/text()": "productId",
    "name/text()": "name",
    "type/text()": "type",
    "regularPrice/text()": "regularPrice",
    "salePrice/text()": "salePrice",
    "onSale/text()": "onSale",
    "salesRankShortTerm/text()": "salesRankShortTerm",
    "salesRankMediumTerm/text()": "salesRankMediumTerm",
    "salesRankLongTerm/text()": "salesRankLongTerm",
    "bestSellingRank/text()": "bestSellingRank",
    "url/text()": "url",
    "categoryPath/*/name/text()": "categoryPath",  # Note the match all here to get the subfields
    "categoryPath/*/id/text()": "categoryPathIds",  # Note the match all here to get the subfields
    "categoryPath/category[last()]/id/text()": "categoryLeaf",
    "count(categoryPath/*/name)": "categoryPathCount",
    "customerReviewCount/text()": "customerReviewCount",
    "customerReviewAverage/text()": "customerReviewAverage",
    "inStoreAvailability/text()": "inStoreAvailability",
    "onlineAvailability/text()": "onlineAvailability",
    "releaseDate/text()": "releaseDate",
    "shortDescription/text()": "shortDescription",
    "class/text()": "class",
    "classId/text()": "classId",
    "department/text()": "department",
    "departmentId/text()": "departmentId",
    "bestBuyItemId/text()": "bestBuyItemId",
    "description/text()": "description",
    "manufacturer/text()": "manufacturer",
    "modelNumber/text()": "modelNumber",
    "image/text()": "image",
    "longDescription/text()": "longDescription",
    "longDescriptionHtml/text()": "longDescriptionHtml",
    "features/*/text()": "features"  # Note the match all here to get the subfields
}

def get_opensearch():
    host = 'localhost'
    port = 9200
    auth = ('admin', 'admin')
    #### Step 2.a: Create a connection to OpenSearch
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,
        http_auth=auth,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False
    )
    return client


def index_file(file, index_name):
    docs_indexed = 0
    client = get_opensearch()
    logger.info(f'Processing file : {file}')
    tree = etree.parse(file)
    root = tree.getroot()
    children = root.findall("./product")
    docs = []
    for child in children:
        doc = {}
        for xpath_expr, key in mappings.items():
            doc[key] = child.xpath(xpath_expr)
        #print(doc)
        if 'productId' not in doc or len(doc['productId']) == 0:
            continue
        #### Step 2.b: Create a valid OpenSearch Doc and bulk index 2000 docs at a time
        docs.append({ '_index': index_name, '_id': doc['sku'][0], '_source': doc })
        if len(docs) >= 2000:
            bulk(client, docs)
            docs = []
    if docs:
        bulk(client, docs)

    return docs_indexed

@click.command()
@click.option('--source_dir', '-s', help='XML files source directory')
@click.option('--index_name', '-i', default="bbuy_products", help="The name of the index to write to")
@click.option('--workers', '-w', default=8, help="The number of workers to use to process files")
def main(source_dir: str, index_name: str, workers: int):
    files = glob.glob(source_dir + "/*.xml")
    docs_indexed = 0
    start = perf_counter()
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(index_file, file, index_name) for file in files]
        for future in concurrent.futures.as_completed(futures):
            docs_indexed += future.result()

    finish = perf_counter()
    logger.info(f'Done. Total docs: {docs_indexed} in {(finish - start)/60} minutes')

if __name__ == "__main__":
    main()
