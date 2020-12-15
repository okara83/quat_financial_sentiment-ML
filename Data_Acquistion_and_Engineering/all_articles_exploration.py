#!/usr/bin/env python3
# -*- coding: utf-8 -*-


####################################
### Neccessary Import Statements ###
####################################
import os
import feedparser
import pandas as pd
import numpy as np


###################################
### Define Neccessary Functions ###
###################################
# Compile a list of all of the RSS links we will be parsing.
FILE_PATH = os.path.dirname(__file__)
REL_PATH_TO_SOURCES = "../Data/news_sources.txt"
PATH_TO_SOURCES = os.path.join(FILE_PATH, REL_PATH_TO_SOURCES)
news_sources_file = open(PATH_TO_SOURCES)
news_sources_raw_list = news_sources_file.read().split("\n")
news_sources_file.close()

raw_rss_feed_links_list = [
	line for line in news_sources_raw_list \
	if line[:3:] == "RSS" and not "easily" in line
]
rss_feed_links_list = [feed.split()[-1] for feed in raw_rss_feed_links_list]

# Parse those links. That is, get the information that we are interested
# in from all of these articles. NOTE that the final result is a list of
# lists which are each populated by dictionaries. Each nested list
# corresponds to a different RSS feed and each dictionary in those lists
# corresponds to a different article in that particular feed.
parsed_list = [
	feedparser.parse(rss_link).entries for rss_link in rss_feed_links_list
]
extracted_dicts_list = [
	[{"title": entry.get("title", None),
	  "url": entry.get("link", None),
	  "description": entry.get("summary", None),
	  "time_stamp": entry.get("published", None),
	  "article_tags": [
	  	  tag_dict.get("term", None) for tag_dict in entry.get("tags", {})
	  ]} \
	  for entry in parsed] for parsed in parsed_list if parsed != []
]

# Now check to see how many of these parsed articles mention one of the
# company's (either by name of by their ticker symbol) we have in our
# list of UAE companies.
REL_PATH_TO_CSV = "../Data/UAE_Markets.csv"
PATH_TO_CSV = os.path.join(FILE_PATH, REL_PATH_TO_CSV)
uae_companies_df = pd.read_csv(PATH_TO_CSV)
company_names_list = uae_companies_df["Company title"].tolist()
company_tickers_list = uae_companies_df["Symbol"].tolist()

total_num_of_articles = sum(
	[len(feed_dicts) for feed_dicts in extracted_dicts_list]
)

num_articles_with_description = 0
num_articles_with_tag = 0
num_articles_with_UAE_company = 0
company_dict = {"Company_Name": [],
                "Company_Ticker": [],
                "Num_Mentioned": [],
                "Num_With_Description": []}
for feed_dicts in extracted_dicts_list:
	# Iterate over each of the RSS feeds that we have.
	for article_dict in feed_dicts:
		# Iterate over each of the articles that we have collected data
		# for in this feed.

		# With the information in this dictionary, check to see how we
		# should update the quantities that we are interested in.
		article_description = article_dict.get("description", None)
		article_tags = article_dict.get("article_tags", None)
		article_title = article_dict.get("title", None)

		# Check description.
		description_checker = all([
			not isinstance(article_description, type(None)),
			article_description != "",
			article_description != " "
		])
		will_be_counted_descr = 1 if description_checker else 0
		num_articles_with_description += will_be_counted_descr

		# Check tags.
		tag_checker = all([
			not isinstance(article_tags, type(None)),
			len(article_tags) > 0,
			all([tag != "" and tag != " " for tag in article_tags])
		])
		will_be_counted_tag = 1 if tag_checker else 0
		num_articles_with_tag += will_be_counted_tag

		# Check for companies in title.
		company_checker_dict = {
			"{}-{}".format(company_name, ticker): \
			company_name.lower() in article_title.lower() \
			or ticker.lower() in article_title.lower()  \
			for company_name, ticker in \
			zip(company_names_list, company_tickers_list)
		}
		if sum(list(company_checker_dict.values())) > 0:
			# If the article title that you are working DOES in fact 
			# mention one of the UAE companies (either by name or by 
			# ticker) we are working with.
			will_be_counted_comp = 1

			mentioned_companies_list = [ 
				key.split("-") for key, value in \
				company_checker_dict.items() if value
			]
			for company_name, ticker in mentioned_companies_list:
				# Iterate over all of the company name, ticker pairs that
				# correspond to the companies that got mentioned in the
				# title of the article we are currently working with.
				try:
					# If this passes, then we know that we have come
					# accross a previous article that mentioned this
					# particular company (either by name or ticker).
					name_index = company_dict["Company_Name"].index(
						company_name
					)
					ticker_index = company_dict["Company_Ticker"].index(
						ticker
					)
					assert name_index == ticker_index

					company_dict["Num_Mentioned"][name_index] += 1
					if will_be_counted_descr:
						company_dict["Num_With_Description"][name_index] += 1
				except ValueError:
					# If the mentioned company has not yet been saved
					# in the company dictionary.
					company_dict["Company_Name"].append(company_name)
					company_dict["Company_Ticker"].append(ticker)
					company_dict["Num_Mentioned"].append(1)
					if will_be_counted_descr:
						company_dict["Num_With_Description"].append(1)
					else:
						company_dict["Num_With_Description"].append(0)
		else:
			will_be_counted_comp = 0 

		num_articles_with_UAE_company += will_be_counted_comp

# Create Final DataFrame
num_mentioned_list = company_dict["Num_Mentioned"]
num_descr_list = company_dict["Num_With_Description"]
assert np.all(
	np.array(num_mentioned_list) >= np.array(num_descr_list)
)

length_checker = [
	len(company_dict["Company_Name"]) == len(company_dict["Company_Ticker"]),
	len(company_dict["Company_Name"]) == len(company_dict["Num_Mentioned"]),
	len(company_dict["Company_Name"]) == len(company_dict["Num_With_Description"])
]
assert all(length_checker)

company_df = pd.DataFrame(company_dict).sort_values(
	by="Num_Mentioned", 
	ascending=False).reset_index(drop=True)

# Print Results.
if __name__ == "__main__":
	print("Printing results of script.")
	print("---------------------------")
	print(
		"The total number of articles worked with is: {}".format(
			total_num_of_articles
			), 
		end="\n\n"
	)
	print(
		"The total number of articles with a description: {}".format(
			num_articles_with_description
			), 
		end="\n\n"
	)
	print(
		"The total number of articles with tags: {}".format(
			num_articles_with_tag), 
		end="\n\n"
	)
	print(
		"The total number of articles that mention a UAE company: {}".format(
			num_articles_with_UAE_company), 
		end="\n\n"
	)
	print(company_df)




