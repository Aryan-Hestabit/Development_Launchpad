FROM python:3.12-slim

WORKDIR /app

COPY . .

# Install core dependencies first
RUN pip install --no-cache-dir \
    fastapi==0.129.0 \
    uvicorn[standard]==0.41.0 \
    scikit-learn==1.8.0 \
    pandas==3.0.0 \
    numpy==2.3.5 \
    category_encoders==2.9.0 \
    pydantic==2.12.5 \
    python-dotenv==1.2.1

# Install xgboost without optional GPU dependencies
RUN pip install --no-cache-dir --no-deps xgboost==3.2.0 && \
    pip install --no-cache-dir scipy

EXPOSE 8000

WORKDIR /app/deployment

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]