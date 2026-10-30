# Pub'lish

**Pub'lish** is a Python-based application for exploring pubs in the Oxford area. Functionality includes pub-tracking, pub-crawl, and statistics to track your pub'lishes (visits to the pub)!

## Installation & Requirements

- Requires Python 3.12 or later

- Use the package manager [pip](https://test.pypi.org/project/beer-app-adgarnier/) to install **Pub'lish**.

     ```bash
     pip install -i https://test.pypi.org/simple/ beer-app-adgarnier
     ```

## Usage

### Run the App
```python3
beer-app
```
### Get a list of available commands:
Run ```--help``` or ``` command --help```.

Example commands:
```
Launch
  Open the interactive Oxford pub map in your browser.
  Use 'launch --help' for more information.

Load
  Add pubs to the map. Choose from all, visited, or unvisited pubs.
  You can also enter 'load all', 'load visited', or 'load unvisited'.
  Use 'load --help' for more information.

Unload
  Remove the currently loaded pubs from the map.
  Use 'unload --help' for more information.

Search
  Search the loaded pubs using names, roads, locations, sponsors, or other keywords.
  Use 'search --help' for more information.

Visit
  Mark pubs as visited and see the pubs you have already visited.
  Use 'visit --help' for more information.

Stats
  Create a graph showing how many times you have visited each pub.
  Use 'stats --help' for more information.

Crawl
  Create your own pub crawl.
  Use 'crawl --help' for more information.

Quit
  Stop the map server and close PUB'LISH.
```

### Run the App
For more usage information, visit the website [here](https://adgarnier.github.io/beer-app/). 

## License & Disclosures
This project is licensed under the MIT license. See: [MIT](LICENSE).  
Disclosures can be found [here](DISCLOSURES.md).  
For the use of AI in this project, see the [AI Disclosure](AI_DISCLOSURE.md).  

## Acknowledgements
Once upon a time, three brave adventurers set out to map the pubs of Oxford. Andy carried the map, Andrew carried the data, and Josef carried a suspiciously large snack.

Together they built Pub'lish: a noble app for finding pubs, planning crawls, and remembering visits that might otherwise blur into legend. They battled bugs, tangled paths, and the occasional chart that refused to behave. At last, the pubs were plotted, the statistics were poured, and the team celebrated their victory with a well-earned pint—after confirming it was in the dataset, of course.

A special thanks to 'Cold Beer' for the idea and the DTC for the skills to tackle such an important app for the greater Oxford community.
