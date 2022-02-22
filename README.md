# HW3.1
To complete this HW:

1) Fork this repo.
2) Add your code to the "historicalData" override method n 
   synchronous_functions.py (starts on Line 51). Your task is to turn the 'bar' 
   object into a dataframe that plotly's candlestick function will accept. 
   Use the candlestick_plot.ipynb notebook for help in figuring this out!
3) Make reactive inputs for each of the parameters needed by 
   "fetch_historical_data" as indicated in Lines 177 to 184 of app.py. Don't 
   forget -- you'll need to include these new vars in the signatures of the 
   callback and the callback function! I have already done this for 
   'whatToShow' and 'endDateTime', so you can follow that example.
