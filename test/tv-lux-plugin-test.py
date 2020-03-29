from resources.lib.tvlux import TVLuxContentProvider
import pdb

def main():
    provider = TVLuxContentProvider()
    categories = provider.categories()

    for i in range(0, len(categories)):
        c = categories[i]
        print "[{}] {}: url: {}".format(i, c["title"], c['url'])

    # Get items of Relacie
    items = provider.list(categories[1]['url'])

    # Get Relacie[3]
    item = items[3]

    # List of videos of Relacie[3]
    videos = provider.list(item['url'])

    # Try to resolve videos[1]
    resolved = provider.resolve(videos[1])

    pdb.set_trace()


if __name__== "__main__":
    main()