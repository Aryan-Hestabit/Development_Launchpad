# 📌 Purpose of This Document
This document explains the advanced query engine implemented for the Product API.
It serves as: 
- Technical documentation for developers 
- Proof of implementation for evaluation 
- Reference for API consumers 
The query engine enables dynamic searching, filtering, sorting, pagination, and soft deletes using query parameters.

## Base Endpoint
```bash
GET /products
```
This endpoint supports multiple query parameters that can be combined in a single request.
## Dynamic Search
###Description
Supports case-insensitive text search across multiple fields using regular expressions and OR conditions.

### Supported Fields
- name
- description
### Query Parameter
```bash
search=<text>
```
### Example
```bash
GET /products?search=phone
```
### Behavior
- Matches products where name OR description contains the search term 
- Uses regex with case-insensitive matching 

## 🎯 Filtering 
### Price Range Filtering
Parameters
```bash 
minPrice=<number> 
maxPrice=<number>
```
Example 
```bash 
GET /products?minPrice=100&maxPrice=500
```
Behavior
- Returns products priced within the given range 
- Either parameter can be used independently

## Tag-Based Filtering 
Parameter
```bash  
tags=<comma-separated-values>
```
Example 
```bash 
GET /products?tags=apple,samsung
```
Behavior
- Returns products containing any of the specified tags 
- Implemented using $in operator 

## ↕️ Sorting
###Parameter
```bash 
sort=<field>:<order>
```
### Supported Orders
- asc
- desc

### Example
```bash 
GET /products?sort=price:desc
```

### Behavior
- Dynamically sorts results by the specified field and order 
- Defaults to database order if not provided

## 📄 Pagination
### Parameters
```bash 
page=<number>
limit=<number>
```
### Example
```bash 
GET /products?page=2&limit=10
```
### Behavior
- Uses offset-based pagination (skip + limit)
- Helps manage large result sets efficiently

## 🗑️ Soft Delete Mechanism 
###Description
Products are not permanently removed from the database. Instead, a deletedAt timestamp marks records as deleted.

### Delete Endpoint
```bash 
DELETE /products/:id
```

### Behavior
- Sets deletedAt to the current timestamp
- Product remains in the database

### Excluding Deleted Records (Default)
```bash 
GET /products
```
- Returns only products where deletedAt = null

### Including Deleted Records
```bash 
GET /products?includeDeleted=true
```
- Returns both active and soft-deleted products 

##⚠️ Error Handling
### Global Error Format
All API errors follow a consistent response structure: 
```bash 
{ "success": false,
"message": "Error description",
"code": "ERROR_CODE",
"timestamp": "ISO_TIMESTAMP",
"path": "/requested/path" }
```
## 🔗 Combined Query
### Example
```bash 
GET /products?search=phone&minPrice=100&maxPrice=500&tags=apple,samsung&sort=price:desc&page=1&limit=10
```
### Behavior
- Applies search, filters, sorting, and pagination together 
- Excludes soft-deleted records by default 
