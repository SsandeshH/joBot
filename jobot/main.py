from data_extractor import main_scraper
from config import insert_values, conn

def main():
    '''
    Main function that runs every other function
    '''

    print("Starting job scraping process...")
    try:
        
        # scrapes, Cleans And Stores on Postgre .. Run only ocassionally
        main_scraper(insert_values) 
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Commit the transaction and close the connection
        conn.commit()
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()