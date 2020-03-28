from resources.lib.tvlux import TVLuxContentProvider
import pdb

def main():
    provider = TVLuxContentProvider()
    categories = provider.categories()

    for i in range(0, len(categories)):
        c = categories[i]
        print "[{}] {}: url: {}".format(i, c["title"], c['url'])

    items = provider.list(categories[1]['url'])

    item = items[3]

    videos = provider.list(item['url'])

    pdb.set_trace()


if __name__== "__main__":
    main()