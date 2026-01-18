       IDENTIFICATION DIVISION.
       PROGRAM-ID. CUSTOMER-ACCOUNT-MGMT.

       * Legacy COBOL Program for Customer Account Processing
       * Author: Legacy Team
       * Year: 2002

       ENVIRONMENT DIVISION.

       DATA DIVISION.
       WORKING-STORAGE SECTION.

       01  WS-CUSTOMER-RECORD.
           05 WS-CUST-ID        PIC 9(5).
           05 WS-CUST-NAME      PIC X(30).
           05 WS-CUST-BALANCE   PIC 9(7)V99.
           05 WS-CUST-STATUS    PIC X(1).

       01  WS-TRANSACTION-AMT   PIC 9(7)V99.
       01  WS-NEW-BALANCE       PIC 9(7)V99.
       01  WS-MESSAGE           PIC X(50).

       PROCEDURE DIVISION.
       MAIN-PARA.

           DISPLAY "ENTER CUSTOMER ID: ".
           ACCEPT WS-CUST-ID.

           DISPLAY "ENTER CUSTOMER NAME: ".
           ACCEPT WS-CUST-NAME.

           DISPLAY "ENTER CURRENT BALANCE: ".
           ACCEPT WS-CUST-BALANCE.

           DISPLAY "ENTER TRANSACTION AMOUNT: ".
           ACCEPT WS-TRANSACTION-AMT.

           IF WS-TRANSACTION-AMT < 0
               MOVE "D" TO WS-CUST-STATUS
           ELSE
               MOVE "A" TO WS-CUST-STATUS
           END-IF.

           COMPUTE WS-NEW-BALANCE =
               WS-CUST-BALANCE + WS-TRANSACTION-AMT.

           IF WS-NEW-BALANCE < 0
               MOVE "INSUFFICIENT FUNDS" TO WS-MESSAGE
           ELSE
               MOVE "TRANSACTION SUCCESSFUL" TO WS-MESSAGE
           END-IF.

           DISPLAY "CUSTOMER ID      : " WS-CUST-ID.
           DISPLAY "CUSTOMER NAME    : " WS-CUST-NAME.
           DISPLAY "NEW BALANCE      : " WS-NEW-BALANCE.
           DISPLAY "STATUS           : " WS-CUST-STATUS.
           DISPLAY "MESSAGE          : " WS-MESSAGE.

           STOP RUN.
