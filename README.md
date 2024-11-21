
# ** 🐸 Pepecoin Payment Gateway**

Pepecoin Payment Gateway is a Python-based backend server built using FastAPI to handle transactions, monitor payments, and automate order management for applications and merchants accepting Pepecoin cryptocurrency payments.

---

## **Features**

- 🚀 **FastAPI**: High-performance API implementation with OpenAPI documentation.
- 💳 **Payment Processing**: Automatically generate payment addresses, monitor transactions, and confirm payments.
- 🔄 **Order Management**: Create, list, cancel, and track orders with real-time updates.
- 🔧 **Customizable**: Add metadata and descriptions to orders for better tracking.
- 🔒 **Secure**: API key authentication and secure database storage.
- 🔍 **Transaction Monitoring**: Automatic transaction validation with Pepecoin blockchain.

---

## **Installation**

### **Prerequisites**

- Python 3.7+
- A running Pepecoin full node with RPC enabled, or access to a Pepecoin blockchain API.
- PostgreSQL or another supported database.

### **Step 1: Install the Library**

Install the package via pip:

```bash
pip install pepecoin
```

### **Step 2: Set Up Environment Variables**

Create a `.env` file in the project root:

```bash
DATABASE_URL=postgresql://user:password@localhost/pepecoin_db
PEPECOIN_RPC_URL=http://localhost:12345/
PEPECOIN_RPC_USER=your_rpc_username
PEPECOIN_RPC_PASSWORD=your_rpc_password
API_KEY=your_api_key_here
```

### **Step 3: Initialize the Database**

Run database migrations to set up tables:

```bash
alembic upgrade head
```

### **Step 4: Start the Server**

Run the FastAPI server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`.

---


### **Endpoints**

#### **1. Create an Order**

- **POST** `/v1/orders`
- Request:

```json
{
  "amount": 10.5,
  "currency": "PEPE",
  "description": "Purchase of digital artwork",
  "customer_email": "customer@example.com",
  "metadata": {
    "order_number": "12345"
  }
}
```

- Response:

```json
{
  "order_id": "ord_123456789",
  "payment_address": "PpK1q2w3e4r5t6y7u8i9o0pLkJhGfDsA",
  "amount_due": 10.5,
  "amount_paid": 0.0,
  "status": "Pending",
  "created_at": "2023-10-15T12:34:56Z",
  "expires_at": "2023-10-15T13:34:56Z",
  "transactions": [],
  "metadata": {
    "order_number": "12345"
  }
}
```

#### **2. Retrieve Order Details**

- **GET** `/v1/orders/{order_id}`
- Response:

```json
{
  "order_id": "ord_123456789",
  "payment_address": "PpK1q2w3e4r5t6y7u8i9o0pLkJhGfDsA",
  "amount_due": 10.5,
  "amount_paid": 10.5,
  "status": "Paid",
  "created_at": "2023-10-15T12:34:56Z",
  "expires_at": "2023-10-15T13:34:56Z",
  "transactions": [
    {
      "txid": "b6f6991d3c...e8e8e8e8e8",
      "amount": 10.5,
      "confirmations": 3,
      "timestamp": "2023-10-15T12:35:00Z"
    }
  ],
  "metadata": {
    "order_number": "12345"
  }
}
```

#### **3. List Orders**

- **GET** `/v1/orders`
- Query Parameters:
  - `status` (Optional): Filter by order status (e.g., `Pending`, `Paid`).
  - `limit` (Optional): Number of results to return (default: 20).
  - `offset` (Optional): Pagination offset (default: 0).

#### **4. Cancel an Order**

- **DELETE** `/v1/orders/{order_id}`
- Response:

```json
{
  "order_id": "ord_123456789",
  "status": "Cancelled"
}
```

---

## **Development**

### **Project Structure**

```plaintext
pepecoin_payment_gateway/
├── app/
│   ├── main.py              # Entry point of the application
│   ├── api/                 # API routes and dependencies
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas for requests/responses
│   ├── services/            # Business logic and Pepecoin node interactions
│   ├── db.py                # Database initialization
│   ├── config.py            # Configuration and environment variables
│   └── utils.py             # Helper utilities
├── alembic/                 # Database migrations
├── tests/                   # Unit and integration tests
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
├── .env                     # Environment variables (do not commit this!)
└── .gitignore               # Git ignore file
```

### **Testing**

1. Install testing dependencies:

```bash
pip install pytest pytest-cov
```

2. Run tests:

```bash
pytest --cov=app tests/
```

---

## **Deployment**

### **Docker Deployment**

Use Docker to containerize the application for easier deployment.

1. Build the Docker image:

```bash
docker build -t pepecoin-payment-gateway .
```

2. Run the container:

```bash
docker run -p 8000:8000 --env-file .env pepecoin-payment-gateway
```

### **Production Ready**

- Use **Gunicorn** with Uvicorn workers for production.
- Deploy behind a reverse proxy (e.g., Nginx) for SSL termination.

---

## **Contributing**

Contributions are welcome! Follow these steps to contribute:

1. Fork the repository.
2. Create a new feature branch: `git checkout -b feature/my-feature`.
3. Commit your changes: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature/my-feature`.
5. Open a pull request.

---

## **License**

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## **Acknowledgments**

- Thanks to the **Pepecoin** community for blockchain insights.
- Built with ❤️ using FastAPI.

---



