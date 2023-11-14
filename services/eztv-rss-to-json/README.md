# EZTV RSS TO JSON

`eztv-rss-to-json` is an entrypoint into a larger system and should be used as such. 

The code is very simple - it reaches out to the eztv services and gets the latest rss feed, normalizes each entry into a `Shows` struct, which it then converts into to JSON. 

Afterward, it then prints the shows to standard out.

The code is intentionally written as a microservice, eventually it may use gRPC for communication between services, but today it uses standard linux piped.

## Limitations

* Not capturing the pubdate. As a result you have to ensure you don't process the same doucment multiple times.

* This implementation is LOSSY - meaning we only get the data that we anticipate needing and shed the rest.

* Parsing of the show metadata is done elsewhere. That means that when a new release comes out you're going to have multiple versions of it.

* Doing anything with this data is an exercise left to anything downstream from here





