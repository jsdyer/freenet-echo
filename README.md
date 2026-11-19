# FreeNet Echo

[FreeNet Echo](https://coolcode.ca/freenet-echo/) · [CoolCode](https://coolcode.ca/)

Compare archived homepages and documented services of community networks in Halifax, Vancouver and Ottawa.

<!-- coolcode:guide -->
Pick Halifax and Vancouver, then select a year to compare the available homepage captures. Follow a dated snapshot or inspect the source explaining when each network offered a service.
<!-- /coolcode:guide -->

## Where the record starts

The source index contains 5,649 successful HTML homepage responses at launch, across the three networks from October 1996 through October 2026. Pick 2000 to see 18 Halifax captures, 20 Vancouver captures and 35 Ottawa captures. Vancouver’s February homepage sample mentions both email and telnet. The milestones separately document the Vancouver network’s move to a web-based community information and hosting system by 1996. Each date can be inspected at the Wayback Machine.

The calendar compares the two chosen networks across years, with links to each year’s earliest and latest qualifying capture. Open either capture to inspect its actual visual appearance. Content digests distinguish unique archived response bodies within that year. Repeated captures remain visible in the count. The selected text samples show archived titles, recognized service terms and differences from an earlier sampled page. A term can disappear from a homepage while the network continues offering the service.

## Data and refresh

The importer queries [Internet Archive’s CDX index](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server) for exact homepage URLs, status 200 and HTML type. It includes bare/“www” aliases, Vancouver’s www2 homepage, Ottawa’s earlier Carleton domain, and Ottawa’s current /en/ homepage. It deduplicates capture records across queries. Redirects and other homepage paths are outside the counts. Archive coverage and versions do not measure public use. Visits to a replay leave CoolCode and load the archive.

Once a month, the job refreshes the index and checks selected representative captures for a short list of service terms. Failed text retrieval leaves that capture available to open. No complete page or page image is mirrored here.

The launch dates and documented milestones come from the communities’ own publications. [Chebucto history](https://chebucto.ns.ca/Chebucto/Membership/history.html) · [VCN’s VolNet history](https://www.vcn.bc.ca/volnet/int.htm) · [NCF’s 1993 project history](https://www.ncf.ca/ncf/freeport2html/papers/history.html).

## Development

Run `python scripts/refresh.py` to retrieve public data, `node --test tests/*.test.mjs` and `python -m unittest discover -s tests` to test, and `python scripts/build.py` to build offline. Serve `dist/` over HTTP. GitHub Actions exercises the main user interaction on Chromium before publishing to Pages. A scheduled import that fails validation does not replace the published edition.
