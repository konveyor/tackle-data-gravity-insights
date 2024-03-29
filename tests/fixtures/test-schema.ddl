
CREATE TABLE HOLDINGEJB (
  PURCHASEPRICE DECIMAL(14, 2),
  HOLDINGID INTEGER NOT NULL PRIMARY KEY,
  QUANTITY DOUBLE NOT NULL,
  PURCHASEDATE TIMESTAMP,
  ACCOUNT_ACCOUNTID INTEGER,
  QUOTE_SYMBOL VARCHAR(250)
);

CREATE TABLE ACCOUNTPROFILEEJB (
  ADDRESS VARCHAR(250),
  PASSWD VARCHAR(250),
  USERID VARCHAR(250) NOT NULL PRIMARY KEY,
  EMAIL VARCHAR(250),
  CREDITCARD VARCHAR(250),
  FULLNAME VARCHAR(250)
);

CREATE TABLE QUOTEEJB (
  LOW DECIMAL(14, 2),
  OPEN1 DECIMAL(14, 2),
  VOLUME DOUBLE NOT NULL,
  PRICE DECIMAL(14, 2),
  HIGH DECIMAL(14, 2),
  COMPANYNAME VARCHAR(250),
  SYMBOL VARCHAR(250) NOT NULL PRIMARY KEY
);

CREATE UNIQUE INDEX QUOTE_SYM ON QUOTEEJB(SYMBOL);   

CREATE TABLE KEYGENEJB (
  KEYVAL INTEGER NOT NULL,
  KEYNAME VARCHAR(250) NOT NULL PRIMARY KEY
);

INSERT INTO KEYGENEJB (KEYNAME,KEYVAL) VALUES ('account', 0);
INSERT INTO KEYGENEJB (KEYNAME,KEYVAL) VALUES ('holding', 0);
INSERT INTO KEYGENEJB (KEYNAME,KEYVAL) VALUES ('order', 0);
  
CREATE TABLE ACCOUNTEJB (
  CREATIONDATE TIMESTAMP,
  OPENBALANCE DECIMAL(14, 2),
  LOGOUTCOUNT INTEGER NOT NULL,
  BALANCE DECIMAL(14, 2),
  ACCOUNTID INTEGER NOT NULL PRIMARY KEY,
  LASTLOGIN TIMESTAMP,
  LOGINCOUNT INTEGER NOT NULL,
  PROFILE_USERID VARCHAR(250)
);

CREATE TABLE ORDEREJB (
  ORDERFEE DECIMAL(14, 2),
  COMPLETIONDATE TIMESTAMP,
  ORDERTYPE VARCHAR(250),
  ORDERSTATUS VARCHAR(250),
  PRICE DECIMAL(14, 2),
  QUANTITY DOUBLE NOT NULL,
  OPENDATE TIMESTAMP,
  ORDERID INTEGER NOT NULL PRIMARY KEY,
  ACCOUNT_ACCOUNTID INTEGER,
  QUOTE_SYMBOL VARCHAR(250),
  HOLDING_HOLDINGID INTEGER,
  FOREIGN KEY (QUOTE_SYMBOL) REFERENCES QUOTEEJB(SYMBOL)
);


ALTER TABLE HOLDINGEJB VOLATILE;
ALTER TABLE ACCOUNTPROFILEEJB VOLATILE;
ALTER TABLE QUOTEEJB VOLATILE;
ALTER TABLE KEYGENEJB VOLATILE;
ALTER TABLE ACCOUNTEJB VOLATILE;
ALTER TABLE ORDEREJB VOLATILE;

CREATE INDEX ACCOUNT_USERID ON ACCOUNTEJB(PROFILE_USERID);
CREATE INDEX HOLDING_ACCOUNTID ON HOLDINGEJB(ACCOUNT_ACCOUNTID);
CREATE INDEX ORDER_ACCOUNTID ON ORDEREJB(ACCOUNT_ACCOUNTID);
CREATE INDEX ORDER_HOLDINGID ON ORDEREJB(HOLDING_HOLDINGID);
CREATE INDEX CLOSED_ORDERS ON ORDEREJB(ACCOUNT_ACCOUNTID,ORDERSTATUS);
