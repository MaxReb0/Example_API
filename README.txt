******** README ********

DESCRIPTION:
    This is a simple Rest API. It is written in Python and uses Flask.
    The purpose of this API is to process loans, payments, and refunds.
    This is a simple implementation that mainly functions as a proof of concept.

    The data for these requests are stored in a local SQL database using flask_sqlalchemy.

INSTALLATION:
    To install the application and get it running, follow these steps:
    
    1.) Change directory into the first level of the project ( the one with the Makefile. )

    2.) Run this command in your terminal: " make venv "
        this will create a virtual environment where all of the necessary libraries will be installed.
    
    3.) If the environment is created correctly, it will print out the command and the path needed to 
        source the environment. Run that.
    
    4.) Now that your environment has been created, you need to install the libraries.
        run "make install".
    
    5.) Now your environment should be built correctly. Run "make test" to run the pytests and 
        verify that everything is functioning as intended.
    
    6.) Now that that is done, run "make run" to start up the server.

FUNCTIONALITY:
    The API has routes for loans, payments, and refunds.

    LOANS:
        All of the loan routes are preceeded by '/loan' in the path.

        CREATE_LOAN:
            PATH: {server}/loan/
            METHOD: POST

            The purpose of this function is to take in a JSON request that will be processed
            and append a loan to the loan table in the database. The goal here is that it
            will eventually be linked to the User that initiated the loan, as well as the 
            attempts to pay off the loan.
            Expects JSON of format:
            {
                "loan_amount" : <amount being requested for loan.>
            }
        
        GET_LOAN:
            PATH: {server}/loan/
            METHOD: GET
        
            This function is used to get a loan. This API currently only supports
            paying off loans, and not other types of payments. 
            It just expects a JSON of the following format:
            {
                'id' :  <id of loan>
            }
    
    PAYMENTS:
        All of the payment routes are preceeded by '/payment' in the path

        CREATE_PAYMENT:
            PATH: {server}/payment/
            METHOD: POST

            This function is used to make a payment. This API currently only supports
            paying off loans, and not other types of payments. If the payment requested
            is larger than the amount owed, it will be refunded. If it is less, it will
            simply process the payment and remove the amount owed. If the loan doesn't exist,
            it will simply return a 400 status code.
            It expects a JSON of the following format
            {
                "loan_id" : <loan_id of loan being payed.>
                "payment_amount" : <amount of loan being payed off>
            }

        GET_PAYMENT:
            PATH: {server}/payment/
            METHOD: GET

            This function is used to get a payment. This API currently only supports
            paying off loans, and not other types of payments. 
            It just expects a JSON of the following format:
            {
                'payment_id' :  <id of payment>
            }

    REFUNDS:
        All of the payment routes are preceeded by '/payment' in the path

        REQUEST_REFUND:
            PATH: {server}/refund/
            METHOD: POST

            This function takes a payment id and attempts to refund it. If the payment
            has already been refunded it will return an error.
            It expects a JSON of this format:
            {
                'payment_id' : <id of payment>
            }