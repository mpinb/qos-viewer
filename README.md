# Slurm QOS Viewer

A user-friendly command-line utility for displaying Slurm Quality of Service (QOS) configurations in a clean, readable, and highly formatted manner.

## Motivation

By default, the `sacctmgr show qos` command in Slurm produces output that is incredibly difficult to parse visually. The default terminal formatting results in sparse matrices, aggressively truncated QOS names, and an overwhelming number of irrelevant columns depending on a user's specific access levels. 

This tool acts as a wrapper around the parsable output of `sacctmgr`, dynamically filtering out empty columns, preventing name truncation, and offering tailored views so researchers and users can easily understand their submission limits and cluster resources.

## Features

* **No Truncation:** Fetches parsable data directly from Slurm, ensuring long QOS names are fully visible.
* **Dynamic Filtering:** Automatically identifies and hides columns that are completely empty or unconfigured across the queried QOS list.
* **Multiple Views:** Offers both a compact tabular view and a detailed row-by-row block view.
* **Built-in Examples:** Provides quick-reference examples for using QOS in Slurm job submissions.

## Installation

You can install the QOS Viewer directly from PyPI using pip:

```bash
pip install qos-viewer