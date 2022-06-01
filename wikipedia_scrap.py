import requests
from bs4 import BeautifulSoup
import pandas as pd
import math 

class ScrapStocksInfo():
    def __init__(self) -> None:
        self.url = "https://en.wikipedia.org/wiki/List_of_most_valuable_companies_in_India"

    def __extract_name_mcap(self, quartely_column):
        '''
        Company name  Market cap info contained in it. Need to extract from them.
        '''
        name_mcap_tuple_list = []
        for i,content in quartely_column.iteritems():
            if type(content) == float and math.isnan(content):
                continue
            company_name = ""
            m_cap = ""
            for j in range(len(content)):
                if content[j].isalpha() or content[j] == " ":
                    company_name += content[j]
                else:
                    m_cap += content[j]
            # removes whitespaces after the word in string
            company_name = company_name.rstrip()
            name_mcap_tuple_list.append((company_name,m_cap))
        
        return name_mcap_tuple_list

    def scrap_web_page(self):
        '''
        It scraps wiki page about most valuable companies in india info.
        
        Assumptions taken - 
        - For Year 2018, no quarter specific data has been given, hence its 
        market cap is in 'Market Capitalizations' column. 
        - For year 2016-17, 2017-18 year tables, quarterly mcaps has been given,
        hence mcap data is stored in particualr Q1/Q2/Q3/Q4 column repsectively.

        Returns - Dataframe consisting of following columns - 
        ['Year','Name','Market Capitalizations','Q1','Q2','Q3','Q4']


        '''
        r = requests.get(url = self.url)
        soup = BeautifulSoup(r.content, "lxml")
        results = soup.find(id="mw-content-text")
        table_list = results.find_all("table", class_="wikitable")
        year_header_list=results.find_all("span",class_="mw-headline")

        master_table_cols = ['Year','Name','Market Capitalizations','Q1','Q2','Q3','Q4']
        master_df_chunks_list = []
        
        for l in range(len(table_list)): 
            table_year=year_header_list[l].text
            dfs = pd.read_html(str(table_list[l]))
            df=dfs[0]
            df.drop('Rank', axis=1, inplace=True)
            source_table_cols = df.columns

            # 2018 table extraction
            # Columns of source table - Company name, Market capitalization(Rs Cr) 
            if l == 0:
                df.columns = ['Name', 'Market Capitalizations']
                df = df.reindex(columns=master_table_cols)
                df['Year'] = table_year
                master_df_chunks_list.append(df)

            # 2016-17 and 2017-18 Year extraction
            # Columns of source table - First quarter(Rs cr), Second quarter(Rs cr), Third quarter(Rs cr), Fourth quarter(Rs cr)
            # where each cell value is Company name  Market cap info contained in it. Need to extract from them.
            else:
                source_destination_quarter_col_map = {"First quarter(Rs cr)":"Q1", "Second quarter(Rs cr)":"Q2", 
                                                        "Third quarter(Rs cr)":"Q3", "Fourth quarter(Rs cr)":"Q4"}
                year_wise_df = pd.DataFrame()
                for col in source_table_cols:
                    name_mcap_tuple_list = self.__extract_name_mcap(df[col])
                    master_table_col_name = source_destination_quarter_col_map[col]
                    if name_mcap_tuple_list:
                        quarter_df = pd.DataFrame(name_mcap_tuple_list, columns=['Name', master_table_col_name])
                        if year_wise_df.empty:
                            year_wise_df = quarter_df
                        else:
                            year_wise_df = quarter_df.merge(year_wise_df, on='Name', how='outer')

                year_wise_df['Year'] = table_year
                year_wise_df = year_wise_df.reindex(columns=master_table_cols)
                master_df_chunks_list.append(year_wise_df)

        master_table = pd.concat(master_df_chunks_list, ignore_index=True, axis=0)
        return master_table  

if __name__ == "__main__":
    scrap_stocks = ScrapStocksInfo()
    master_table = scrap_stocks.scrap_web_page()
    master_table.to_csv("Mcap_scrapped_data.csv")
