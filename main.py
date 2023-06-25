import argparse
from module import *
from image_crawler import ImageCrawler

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pixiv", action="store_true", help="activate the pixiv option"
    )
    args = parser.parse_args()

    # If --pixiv is used, run ImageCrawler with input artist_id
    if args.pixiv:
        while True:
            artist_id = input("Please input artist id: ")
            if artist_id.isdigit():
                crawler = ImageCrawler(artist_id)
                crawler.run()
                break
            else:
                print("Invalid artist id.")

    # If --pixiv is not used, run ImageProcessor
    else:
        # Create an instance of the ImageProcessor class
        processor = ImageProcessor()

        # Process the images
        processor.process_images()
