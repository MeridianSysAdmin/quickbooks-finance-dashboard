IF DB_ID('FinanceDemo') IS NULL CREATE DATABASE FinanceDemo;
GO
USE FinanceDemo;
GO

CREATE TABLE dbo.Customer (
    Id           NVARCHAR(20)  NOT NULL PRIMARY KEY,
    DisplayName  NVARCHAR(200) NULL,
    Balance      DECIMAL(18,2) NULL,
    Active       BIT           NULL,
    LoadedAt     DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.Invoice (
    Id           NVARCHAR(20)  NOT NULL PRIMARY KEY,
    DocNumber    NVARCHAR(50)  NULL,
    CustomerId   NVARCHAR(20)  NULL,
    TxnDate      DATE          NULL,
    DueDate      DATE          NULL,
    TotalAmt     DECIMAL(18,2) NULL,
    Balance      DECIMAL(18,2) NULL,
    LoadedAt     DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.Account (
    Id              NVARCHAR(20)  NOT NULL PRIMARY KEY,
    Name            NVARCHAR(200) NULL,
    AccountType     NVARCHAR(100) NULL,
    Classification  NVARCHAR(50)  NULL,
    CurrentBalance  DECIMAL(18,2) NULL,
    Active          BIT           NULL,
    LoadedAt        DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);