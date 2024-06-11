# Cloud Integrated Habitat Monitoring API

This is my take on the Full Stack Engineering Challenge made utilizing vanilla Python 3.10, AWS Lambda, API Gateway, and DynamoDB.  

## Rationale behind DynamoDB Schemas

The DynamoDB table for this project has two primary attributes: `HabitatID` and `Date`. These attributes serve as the composite primary key, where `HabitatID` is the partition key and `Date` is the sort key. This design allows efficient querying of data for a specific habitat over time.

Additionally, there are three other attributes that are enforced through the Lambda function: `DataType`, `DataValue`, and `SensorID`. These attributes are essential for the integrity and utility of the data stored in the table. When a new item is POSTed into the database, the Lambda function validates that all five attributes are present before adding the item. This ensures that each entry is complete and consistent.

### Reasons for Choosing This Schema Design

1. **Efficient Querying**: The combination of `HabitatID` and `Date` as the primary key allows for efficient querying of data related to a specific habitat over a period of time. This is particularly useful for applications that need to track changes or trends in habitat data.

2. **Data Integrity**: By making `DataType`, `DataValue`, and `SensorID` mandatory through the Lambda function, we ensure that every entry is meaningful and usable. `DataType` specifies what kind of data is being recorded (e.g., temperature, humidity), `DataValue` holds the actual measurement, and `SensorID` identifies the source of the data. This level of detail is crucial for accurate data analysis and reporting.

3. **Scalability**: DynamoDB is designed to scale horizontally, and by using `HabitatID` as the partition key, we can distribute the data across multiple partitions. This enhances the table's ability to handle high volumes of read and write operations, ensuring performance remains optimal as the dataset grows.

4. **Flexibility for Future Enhancements**: The schema is designed with flexibility in mind, allowing for additional attributes to be added in the future if needed. This can be done without significant changes to the existing schema or the Lambda function, facilitating easy expansion of the application's capabilities.

5. **Data Consistency and Validation**: Implementing mandatory checks in the Lambda function before writing data to the table ensures that the database remains consistent. This reduces the risk of incomplete or incorrect data entries, which is critical for maintaining the reliability of the application's data.

By carefully designing the schema and incorporating validation through the Lambda function, we achieve a robust and scalable database solution that meets the needs of the application while ensuring data integrity and performance.

## Summary of the Security System Put in Place

To ensure the security and integrity of the Habitat Data API, several security measures have been implemented:

### API Key Validation

In order for the API to be called, a valid API key must be provided. This is a crucial step in securing the API endpoints and preventing unauthorized access. The API key acts as a unique identifier for each client application, allowing the system to:

1. **Authenticate Requests**: Each request to the API must include a valid API key in the headers. This key is checked against a list of authorized keys stored securely, ensuring that only trusted clients can access the API.

2. **Rate Limiting**: By associating each API key with a specific client, we can implement rate limiting to prevent abuse. This means that even if a key is compromised, the potential damage is limited to the constraints set for that key, such as the number of requests per minute.

3. **Monitoring and Logging**: API key usage is logged, allowing for detailed monitoring of API access patterns. This helps in detecting and responding to suspicious activities, such as a spike in requests from a single key, which could indicate a security breach.

### IAM Roles and Policies

The Lambda function and other AWS resources are secured using IAM roles and policies:

1. **Least Privilege Principle**: The Lambda function is assigned an IAM role that grants it only the permissions it needs to perform its tasks. This role includes permissions to read from and write to the DynamoDB table but does not allow any other actions.

2. **Managed Policies**: The IAM role uses AWS managed policies, such as `AmazonDynamoDBFullAccess`, ensuring that best practices for security are followed. Managed policies are regularly updated by AWS to incorporate new security measures.

### Encryption

Data is encrypted at rest and in transit to protect it from unauthorized access and tampering:

1. **Encryption at Rest**: The DynamoDB table data is encrypted at rest using AWS managed keys. This ensures that even if the underlying storage is compromised, the data remains secure.

2. **Encryption in Transit**: All data transmitted between clients and the API, as well as between the Lambda function and DynamoDB, is encrypted using HTTPS and SSL/TLS protocols. This protects the data from interception and eavesdropping.

### Access Control

Access to the API and AWS resources is tightly controlled:

1. **API Gateway Authorization**: API Gateway is configured to use API key-based authorization. This setup ensures that each API call is authenticated and authorized before being processed.

2. **Lambda Function Access**: The Lambda function can only be invoked by authorized API Gateway endpoints. This prevents direct access to the function from unauthorized sources.

## Cost and Scalability Analysis

### Cost Analysis

The costs associated with the deployment and operation of the Habitat Data API primarily stem from the following AWS services:

1. **AWS Lambda**:
    - **Execution Duration**: AWS Lambda pricing is based on the number of requests and the execution duration. Costs are calculated based on the number of function invocations and the time it takes to run your code. The default memory allocation is 128 MB, but it can be adjusted to optimize cost and performance.

2. **Amazon DynamoDB**:
    - **Provisioned Throughput**: DynamoDB pricing is based on the provisioned read and write capacity units. The table in our template is set to 5 read and write capacity units, which incurs a predictable monthly cost.
    - **Storage Costs**: DynamoDB charges for the amount of data stored in the table. The cost is calculated per GB per month.
    - **Global Secondary Indexes (GSI)**: Additional costs are incurred for each GSI based on the provisioned throughput and storage used by the index.

3. **Amazon API Gateway**:
    - **API Requests**: API Gateway pricing is based on the number of API requests received. It includes both the free tier of 1 million requests per month and the usage-based pricing beyond the free tier.
    - **Data Transfer**: Data transfer costs are incurred for data sent to and from the API Gateway.

### Cost Calculation for Daily Records

To estimate costs, we will consider three scenarios: handling 10,000, 100,000, and 1 million daily records.

#### Scenario 1: 10,000 Daily Records

- **AWS Lambda**:
  - Number of requests per month: 10,000 * 30 = 300,000 requests
  - Assuming an average execution duration of 100ms and memory allocation of 128 MB
  - Monthly compute time: 300,000 * 100ms = 30,000 seconds
  - Compute cost: 30,000 seconds * $0.00001667 per GB-second (128 MB = 0.125 GB) = 30,000 * 0.125 * $0.00001667 = $0.0625
  - Request cost: 300,000 requests * $0.20 per million requests = 300,000 / 1,000,000 * $0.20 = $0.06
  - Total Lambda cost: $0.0625 + $0.06 = $0.1225

- **Amazon DynamoDB**:
  - Write capacity units: 10,000 / 86400 = 0.12 (rounded up to 1)
  - Read capacity units: 10,000 / 86400 = 0.12 (rounded up to 1)
  - Monthly cost: $0.47 per WCU and $0.09 per RCU
  - Total DynamoDB cost: $0.47 + $0.09 = $0.56

- **Amazon API Gateway**:
  - Number of requests per month: 300,000 requests
  - Request cost: 300,000 requests * $3.50 per million requests = 300,000 / 1,000,000 * $3.50 = $1.05

**Total Monthly Cost for 10,000 Daily Records: $0.1225 + $0.56 + $1.05 = $1.7325**

#### Scenario 2: 100,000 Daily Records

- **AWS Lambda**:
  - Number of requests per month: 100,000 * 30 = 3,000,000 requests
  - Monthly compute time: 3,000,000 * 100ms = 300,000 seconds
  - Compute cost: 300,000 seconds * $0.00001667 per GB-second (128 MB = 0.125 GB) = 300,000 * 0.125 * $0.00001667 = $0.625
  - Request cost: 3,000,000 requests * $0.20 per million requests = 3,000,000 / 1,000,000 * $0.20 = $0.60
  - Total Lambda cost: $0.625 + $0.60 = $1.225

- **Amazon DynamoDB**:
  - Write capacity units: 100,000 / 86400 = 1.16 (rounded up to 2)
  - Read capacity units: 100,000 / 86400 = 1.16 (rounded up to 2)
  - Monthly cost: $0.94 per WCU and $0.18 per RCU
  - Total DynamoDB cost: $0.94 + $0.18 = $1.12

- **Amazon API Gateway**:
  - Number of requests per month: 3,000,000 requests
  - Request cost: 3,000,000 requests * $3.50 per million requests = 3,000,000 / 1,000,000 * $3.50 = $10.50

**Total Monthly Cost for 100,000 Daily Records: $1.225 + $1.12 + $10.50 = $12.845**

#### Scenario 3: 1 Million Daily Records

- **AWS Lambda**:
  - Number of requests per month: 1,000,000 * 30 = 30,000,000 requests
  - Monthly compute time: 30,000,000 * 100ms = 3,000,000 seconds
  - Compute cost: 3,000,000 seconds * $0.00001667 per GB-second (128 MB = 0.125 GB) = 3,000,000 * 0.125 * $0.00001667 = $6.25
  - Request cost: 30,000,000 requests * $0.20 per million requests = 30,000,000 / 1,000,000 * $0.20 = $6.00
  - Total Lambda cost: $6.25 + $6.00 = $12.25

- **Amazon DynamoDB**:
  - Write capacity units: 1,000,000 / 86400 = 11.57 (rounded up to 12)
  - Read capacity units: 1,000,000 / 86400 = 11.57 (rounded up to 12)
  - Monthly cost: $5.64 per WCU and $1.08 per RCU
  - Total DynamoDB cost: $5.64 + $1.08 = $6.72

- **Amazon API Gateway**:
  - Number of requests per month: 30,000,000 requests
  - Request cost: 30,000,000 requests * $3.50 per million requests = 30,000,000 / 1,000,000 * $3.50 = $105.00

**Total Monthly Cost for 1 Million Daily Records: $12.25 + $6.72 + $105.00 = $123.97**

### Scalability Analysis

The architecture of the Habitat Data API leverages AWS's fully managed services to ensure high scalability and availability:

1. **AWS Lambda**:
    - **Automatic Scaling**: AWS Lambda automatically scales based on the number of incoming requests. It can handle sudden spikes in traffic by provisioning additional instances to meet the demand.
    - **Concurrency Limits**: Lambda supports setting concurrency limits to control the maximum number of simultaneous function executions, which helps manage costs and maintain performance.

2. **Amazon DynamoDB**:
    - **Auto Scaling**: DynamoDB can be configured to automatically adjust the read and write capacity based on the actual workload. This ensures that the table can handle varying levels of traffic without manual intervention.
    - **High Availability**: DynamoDB is designed to be highly available and fault-tolerant, replicating data across multiple Availability Zones.

3. **Amazon API Gateway**:
    - **Throttling and Rate Limiting**: API Gateway allows setting throttling limits to control the rate of incoming requests. This protects backend services from being overwhelmed by high traffic.
    - **Global Distribution**: API Gateway supports deployment in multiple regions, enabling low-latency access for users around the world.

### Cost Optimization Strategies

To manage and optimize costs, consider the following strategies:

1. **Monitoring and Alerts**: AWS CloudWatch can be set up to monitor usage patterns and costs. Alerts can be configured to notify you when usage exceeds predefined thresholds.
2. **API Gateway Caching**: Caching can be enabled in API Gateway to reduce the number of requests sent to the backend, thus lowering the cost of Lambda executions and DynamoDB read operations.
3. **Review and Adjust Provisioned Capacity**: Regularly review the provisioned capacity for DynamoDB and GSIs. Adjust the capacity to match the actual workload to avoid over-provisioning.

By carefully analyzing and monitoring the costs and implementing these optimization strategies, the Habitat Monitoring API can be both cost-effective and highly scalable to meet the demands of varying workloads.




