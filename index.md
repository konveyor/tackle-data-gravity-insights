---
layout: default
title: Home
nav_order: 1
description: "Tackle DGI Introduction"
permalink: /
---

# Tackle Data Gravity Insights

[![Build Status](https://github.com/konveyor/tackle-data-gravity-insights/actions/workflows/ci-build.yml/badge.svg)](https://github.com/konveyor/tackle-data-gravity-insights/actions)
[![PyPI version](https://badge.fury.io/py/tackle-dgi.svg)](https://badge.fury.io/py/tackle-dgi)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Tackle Data Gravity Insights is a new way to gain insights into your monolithic application code so that you can better refactor it into domain driven microservices. It takes a wholistic approach to application modernization and refactoring by triangulating between code, and, data, and transactional boundaries.

Application modernization is a complex topic with refactoring being the most complicated undertaking. Current tools only look at the application source code or only at the runtime traces when refactoring. This, however, yields a myopic view that doesn't take into account data relationships and transactional scopes. This project hopes to join the three views of application, data, and transactions into a 3D view of the all of the application relationships so that you can easily discover application domains of interest and refactor them into microservices. Accordingly, DGI consists of three key components:

**1. Call-/Control-/Data-dependency Analysis (code2graph):** This is a source code analysis component that extracts various static code interaction features pertaining to object/dataflow dependencies and their respective lifecycle information. It presents this information in a graphical format with Classes as _nodes_ and their dataflow, call-return, and heap-dependency interactions _edges_.

**2. Schema:** This component of DGI infers the schema of the underlying databases used in the application. It presents this information in a graphical format with database tables and columns as _nodes_ and their relationships (e.g., foreign key, etc.) as _edges_.

**3. Transactions to graph (tx2graph):** This component of DGI leverages [Tackle-DiVA](https://github.com/konveyor/tackle-diva) to perform a data-centric application analysis. It imports a set of target application source files (*.java/xml) and provides following analysis result files. It presents this information in a graphical format with database tables and classes as _nodes_ and their transactional relationships as _edges_.

![DGI_3D](../../assets/images/DGI_3D.png)