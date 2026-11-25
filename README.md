# FreeNet Echo

[FreeNet Echo](https://coolcode.ca/freenet-echo/) · [CoolCode](https://coolcode.ca/)

Explore Canada’s early community networks and ISP portals through dated homepage captures, service traces and documented milestones.

<!-- coolcode:guide -->
Search seven configurable network/portal profiles, then choose two and a year. Start with VCN and Chebucto, or inspect the early Sympatico and Shaw @Home eras. Milestones cite historical sources and link the nearest saved year-edge capture where one exists. Missing source indexes are labelled unavailable, never zero. Enter another historic domain to prepare archive and Domain Biography links locally.
<!-- /coolcode:guide -->

## Where the record starts

The source index contains 5,649 successful HTML homepage responses at launch, across the original three networks from October 1996 through October 2026. Pick 2000 to see 18 Halifax captures, 20 Vancouver captures and 35 Ottawa captures. Vancouver’s February homepage sample mentions both email and telnet. The milestones separately document the Vancouver network’s move to a web-based community information and hosting system by 1996. Each date can be inspected at the Wayback Machine.

The calendar compares the two chosen networks across years, with links to each year’s earliest and latest qualifying capture. Open either capture to inspect its actual visual appearance. Content digests distinguish unique archived response bodies within that year. Repeated captures remain visible in the count. The selected text samples show archived titles, recognized service terms and differences from an earlier sampled page. A term can disappear from a homepage while the network continues offering the service.

## Data and refresh

The importer queries [Internet Archive’s CDX index](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server) for exact homepage URLs, status 200 and HTML type. It includes bare/“www” aliases, Vancouver’s www2 homepage, Ottawa’s earlier Carleton domain, and Ottawa’s current /en/ homepage. It deduplicates capture records across queries. Redirects and other homepage paths are outside the counts. Archive coverage and versions do not measure public use. Visits to a replay leave CoolCode and load the archive.

Seven profiles are configured: Chebucto, VCN, National Capital FreeNet, Victoria Free-Net, Toronto Free-Net, Sympatico and Shaw’s early cable-internet era. The November 25, 2026 expansion has genuine saved indexes for all seven profiles: 14,128 qualifying capture observations and 41 homepage text samples. Later additions whose archive requests fail stay explicitly unavailable until a successful collection. Each profile shows its own retrieval date; the complete-collection timestamp stays unchanged when only new profiles are seeded. Sympatico is bounded to 1995–2005 and Shaw to 1996–2001 so later domain reuse does not become evidence about the old service.

Once a month, the job refreshes the index and checks selected representative captures for a short list of service terms. Failed text retrieval leaves that capture available to open. No complete page or page image is mirrored here.

The launch dates and documented milestones come from the communities’ own publications. [Chebucto history](https://chebucto.ns.ca/Chebucto/Membership/history.html) · [VCN’s VolNet history](https://www.vcn.bc.ca/volnet/int.htm) · [NCF’s 1993 project history](https://www.ncf.ca/ncf/freeport2html/papers/history.html).

## Expand or customize

Edit `web/config.json`: add a unique `id`, name, city, kind, exact `homepages`, context, source URL and `history` entries (`[date, description, optional source URL]`). Optional `from_year`/`to_year` limit an historical era. `sample_years` controls which saved first responses are read for service terms, and `max_capture_rows` caps each homepage index. Filters, selectors and counts derive from this configuration and the captured data. Tests add another profile beyond the initial seven.

Pushes to `main` automatically attempt to seed configured profiles with no saved index. Their checked/failure timestamps are recorded separately; failure does not advance the complete-refresh date or erase existing records.

Run `python scripts/refresh.py --new-only` to seed new profiles while preserving existing data and the full-refresh date if a source is unavailable. Run `python scripts/refresh.py` for the strict monthly refresh: any failed required index leaves the entire prior edition untouched. Query limits are detected instead of silently truncating counts; narrow an era if necessary. Text-sample failures leave valid index metadata usable. Dates indicate archive observations, not proof that a service launched or ceased then.

The milestone replay links select the closest saved first/last-of-year capture to January 1 of the milestone year and display its actual timestamp. They are navigation aids, not event-date matches. Historical descriptions come from the networks’ publications, the 1995 Canadian Community Networks Directory, BCE’s 2005 annual filing and Shaw’s 2004 filing/1998 CRTC hearing.

No visitor search history is retained. Search and comparison use downloaded JSON locally. Custom domain entry only prepares links; opening one sends that domain to the chosen destination. Archived links go to Internet Archive, not directly to defunct or repurposed domains.

## Development

Run `python scripts/refresh.py` to retrieve public data, `node --test tests/*.test.mjs` and `python -m unittest discover -s tests` to test, and `python scripts/build.py` to build offline. Serve `dist/` over HTTP. GitHub Actions exercises the main user interaction on Chromium before publishing to Pages. A scheduled import that fails validation does not replace the published edition.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. A scheduler on our own Linux server is the planned independent trigger. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->
