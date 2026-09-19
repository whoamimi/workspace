# Customer Segmentation with Deep Learning

## Brief

Not a scored Kaggle competition — an open-ended analytics project built on
the Kaggle dataset [`carrie1/ecommerce-data`](https://www.kaggle.com/datasets/carrie1/ecommerce-data)
(UK online retailer transaction history).

## Objective

Based on a customer's item descriptions and purchase history, build
customer segments that infer shopping-behavior profiles — framed
provocatively as "can you infer their MBTI type from what they buy?" — via:

- Product groups (what they buy)
- Shopping needs (why/how they buy)
- Customer profile segments (behavioral archetype)

Candidate classification/reduction methods considered: hyperplane
methods, K-NN, Self-Organizing Maps (SOM) for clustering; PCA, t-SNE,
UMAP/manifold learning for dimensionality reduction.

## Data

`data.csv` (`carrie1/ecommerce-data`): `InvoiceNo`, `StockCode`,
`Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`,
`Country`.

## Methods Implemented

1. **Item embeddings** — `sentence-transformers/all-MiniLM-L6-v2` encodes
   each `Description` into a dense vector (currently on a 100-row sample).
2. **Cluster count estimation** — K-Means over the embeddings, sweeping
   `k=2..9`, scored with silhouette score (elbow/BIC/DBSCAN considered but
   not yet implemented).
3. **Similarity inspection** — cosine similarity matrix between item
   embeddings, visualized as a heatmap.
4. **Customer-level aggregation** — per `(CustomerID, InvoiceNo)`
   `Quantity`/`UnitPrice` count/sum/mean, as a starting feature set for
   customer-level (vs. item-level) segmentation.

The title references a Self-Organizing Map (SOM) approach; the SOM model
itself is not yet implemented in the notebook — see Extensions.

## Evaluation

No official leaderboard metric (this isn't a scored competition).
Currently self-evaluated via silhouette score on item clusters; customer
segment quality (interpretability, stability) is not yet assessed.

## Results

_Not yet produced — clustering has only been run on a 100-row sample of
item descriptions, not the full customer base._

## Extensions

- Implement the SOM model referenced by the project name; compare against
  the K-Means baseline.
- Scale item embedding beyond the 100-row `SAMPLE_SIZE` sample.
- Build customer-level (not just item-level) feature vectors combining
  embeddings with the `Quantity`/`UnitPrice` aggregates already computed.
- Define a concrete evaluation approach for segment quality beyond
  silhouette score (e.g. business interpretability, label stability across
  runs).
- Split into `notebooks/00_eda.ipynb` + `src/models/` once the approach
  stabilizes.

## References

- [`carrie1/ecommerce-data`](https://www.kaggle.com/datasets/carrie1/ecommerce-data) (Kaggle dataset).
