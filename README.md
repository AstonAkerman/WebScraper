# Introduction

WebScraper is a console program that scrapes all pages and resources from a website, using multiprocessing in order to improve performance.
Be aware that running a webscraper on a website without permission can be interpreted as a [Denial of Service (DoS) attack](https://en.wikipedia.org/wiki/Denial-of-service_attack).

# Installation

WebScraper was created for Windows OS, and has thus not been tested on other operating system softwares.

I recommend using [Anaconda](https://www.anaconda.com/distribution/) or the light-weight version [Miniconda](https://docs.conda.io/en/latest/miniconda.html) to make sure that the correct dependencies are installed. Once installed, create an environment by running the following command. The environment will contain all libraries needed to run the program with default settings. By default, the environment will be named `webscraper`, but you can choose another name using the `-n` option.

    $ conda env create -f environment.yml

Next, activate the environment:

    $ conda activate webscraper

# Start WebScraper

To run Webscraper, run the following command in the project directory `webscraper/` .

    $ python main.py -o <output path for the resulting webpage> -u <url-link to the target website>

## Example

    $ cd webscraper
    $ python main.py -o ./test -u -u http://books.toscrape.com/

## Contact

Feel free to contact me if there are questions about the code:

[Aston Åkerman](https://www.linkedin.com/in/astonakerman/)

## License

```
Copyright 2024-present Aston Åkerman
```

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

```
http://www.apache.org/licenses/LICENSE-2.0
```

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
