---
date: 2025-10-04
author: Oleg Patsay
slug: qdrant-php-client-vector-search
excerpt: "Add vector search to PHP 7.2 and 8.* apps with a simple Qdrant client."
---

# Qdrant PHP Client: Vector Search for PHP 7.2 and 8.*

Many PHP apps still run on PHP 7.2. They cannot upgrade fast. Most new AI tools need PHP 8+. So teams feel stuck. This small library helps. You can add vector search today, even in old projects. It works on PHP 7.2 and also on PHP 8.*.

## What is vector search?

Vector search finds things that are similar in meaning. We turn text or items into numbers (vectors). Then we search by distance between vectors. It is great for semantic search, recommendations, and deduplication.

## How to get vectors (embeddings)

A critical part of vector search is turning your data into vectors. You need neural models that are trained to create vector representations (embeddings) for text, images, or other objects.

- Cloud APIs from major providers. Easy to start and often high quality, but you pay per use and send data over the network.
- Open models that you can run locally or in your own environment. More control and privacy, but you need hardware and setup.
- Specialized services that offer vectorization as a service. Simple integration with some control and SLAs.

Choose based on your quality needs, budget, data privacy rules, and your infrastructure.

## Why legacy PHP needs this

- Many companies cannot upgrade PHP now.
- But they still need AI features.
- Today, most new libraries drop PHP 7.2 support. This is a problem for many sites.
- This client works with PHP 7.2+. It talks to Qdrant server over HTTP.

With this client, you can build modern features without a full rewrite.

## Install

```bash
composer require tenqz/qdrant
```

You also need a Qdrant server (local or cloud). Default port is 6333.

## Quick start

### 1) Create a client

```php
<?php
use Tenqz\Qdrant\QdrantClient;
use Tenqz\Qdrant\Transport\Infrastructure\Factory\CurlHttpClientFactory;

$factory = new CurlHttpClientFactory();
$httpClient = $factory->create("localhost", 6333);
$client = new QdrantClient($httpClient);
```

### 2) Create a collection

You set vector size and distance. Here we use 4 and Cosine for a short demo.

```php
<?php
$client->createCollection("products", 4, "Cosine");
```

### 3) Upsert points (vectors + payload)

```php
<?php
$client->upsertPoints("products", [
    ["id" => 1, "vector" => [0.1, 0.2, 0.3, 0.4], "payload" => ["name" => "T-shirt", "price" => 19]],
    ["id" => 2, "vector" => [0.6, 0.1, 0.8, 0.2], "payload" => ["name" => "Jeans",   "price" => 49]],
]);
```

### 4) Search by vector

```php
<?php
$results = $client->search("products", [0.1, 0.2, 0.3, 0.5], 3);

foreach ($results as $hit) {
    // score, id, payload
    echo $hit["id"] . " " . $hit["score"] . PHP_EOL;
}
```

## Handle errors

```php
<?php
use Tenqz\Qdrant\Transport\Domain\Exception\TransportException;
use Tenqz\Qdrant\Transport\Domain\Exception\HttpException;
use Tenqz\Qdrant\Transport\Domain\Exception\NetworkException;

try {
    $results = $client->search("products", [0.1, 0.2, 0.3, 0.5], 5);
} catch (HttpException $e) {
    echo "HTTP Error {$e->getStatusCode()}: {$e->getMessage()}" . PHP_EOL;
} catch (NetworkException $e) {
    echo "Network Error: {$e->getMessage()}" . PHP_EOL;
} catch (TransportException $e) {
    echo "Error: {$e->getMessage()}" . PHP_EOL;
}
```

## Ideas you can build

- Semantic search for products or docs
- "More like this" recommendations
- Find near-duplicates
- Smart tags and clusters

## Notes

- In real apps, vectors have bigger size (for example, 384 or 768).
- You can add filters (price, category, user id).
- Qdrant can run in Docker. It is easy to start.

## Conclusion

Legacy does not mean "no AI". With this client, PHP 7.2 apps can get vector search now. Start small, ship value, and plan upgrades later.

## Links

- GitHub: [tenqz/qdrant](https://github.com/tenqz/qdrant)
- Research paper on Zenodo: [A PHP Client for Vector Search in Legacy Projects](https://zenodo.org/records/17264965)

---

## Let's make the complex understandable.

Architecture, engineering leadership, and AI in development — when the system is too important to simplify, and too expensive not to own.

**Oleg Patsay**

- Telegram: [t.me/opatsay](https://t.me/opatsay)
- Website: [opatsay.com](https://opatsay.com/)
- [LinkedIn](https://www.linkedin.com/in/oleg-patsay)
- [Email](mailto:opatsay@gmail.com)
