"""
Schema Markup Generator utilities for creating and validating structured data.
"""

import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Any, Optional
import re
from datetime import datetime


class SchemaGenerator:
    """Schema markup generator and validator."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        # Schema.org vocabulary base
        self.schema_base = "https://schema.org/"

        # Common schema types and their required properties
        self.schema_templates = {
            "Organization": {
                "required": ["@type", "name"],
                "recommended": ["url", "logo", "contactPoint", "address", "sameAs"],
                "optional": [
                    "description",
                    "foundingDate",
                    "founder",
                    "numberOfEmployees",
                ],
            },
            "LocalBusiness": {
                "required": ["@type", "name", "address"],
                "recommended": ["telephone", "url", "openingHours", "priceRange"],
                "optional": [
                    "description",
                    "image",
                    "geo",
                    "review",
                    "aggregateRating",
                ],
            },
            "Product": {
                "required": ["@type", "name"],
                "recommended": ["image", "description", "brand", "offers"],
                "optional": ["sku", "mpn", "gtin", "review", "aggregateRating"],
            },
            "Article": {
                "required": ["@type", "headline", "author", "datePublished"],
                "recommended": ["image", "publisher", "dateModified"],
                "optional": ["description", "wordCount", "keywords", "articleSection"],
            },
            "BlogPosting": {
                "required": ["@type", "headline", "author", "datePublished"],
                "recommended": [
                    "image",
                    "publisher",
                    "dateModified",
                    "mainEntityOfPage",
                ],
                "optional": ["description", "wordCount", "keywords", "commentCount"],
            },
            "NewsArticle": {
                "required": [
                    "@type",
                    "headline",
                    "author",
                    "datePublished",
                    "publisher",
                ],
                "recommended": ["image", "dateModified", "mainEntityOfPage"],
                "optional": ["description", "wordCount", "keywords", "dateline"],
            },
            "Event": {
                "required": ["@type", "name", "startDate", "location"],
                "recommended": ["description", "endDate", "organizer", "offers"],
                "optional": [
                    "image",
                    "performer",
                    "url",
                    "eventStatus",
                    "eventAttendanceMode",
                ],
            },
            "Person": {
                "required": ["@type", "name"],
                "recommended": ["url", "image", "jobTitle", "worksFor"],
                "optional": [
                    "description",
                    "birthDate",
                    "address",
                    "sameAs",
                    "knowsAbout",
                ],
            },
            "Recipe": {
                "required": [
                    "@type",
                    "name",
                    "author",
                    "recipeIngredient",
                    "recipeInstructions",
                ],
                "recommended": [
                    "image",
                    "description",
                    "prepTime",
                    "cookTime",
                    "nutrition",
                ],
                "optional": [
                    "recipeYield",
                    "recipeCategory",
                    "recipeCuisine",
                    "keywords",
                ],
            },
            "FAQPage": {
                "required": ["@type", "mainEntity"],
                "recommended": [],
                "optional": ["name", "description"],
            },
            "BreadcrumbList": {
                "required": ["@type", "itemListElement"],
                "recommended": [],
                "optional": ["name", "description"],
            },
        }

    def generate_schema(self, schema_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema markup for the specified type and data."""
        try:
            if schema_type not in self.schema_templates:
                raise ValueError(f"Unsupported schema type: {schema_type}")

            # Generate the schema based on type
            schema_method = getattr(self, f"_generate_{schema_type.lower()}", None)
            if schema_method:
                schema_markup = schema_method(data)
            else:
                schema_markup = self._generate_generic_schema(schema_type, data)

            # Validate the generated schema
            validation_result = self._validate_schema_structure(
                schema_markup, schema_type
            )

            # Format the output
            json_ld = self._format_json_ld(schema_markup)
            microdata = self._generate_microdata_example(schema_markup, schema_type)

            return {
                "schema_markup": schema_markup,
                "json_ld": json_ld,
                "microdata_example": microdata,
                "validation": validation_result,
                "schema_type": schema_type,
                "generation_timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise Exception(f"Schema generation failed: {str(e)}")

    def validate_schema(self, schema_markup: str) -> Dict[str, Any]:
        """Validate existing schema markup."""
        try:
            # Try to parse as JSON
            try:
                schema_data = json.loads(schema_markup)
            except json.JSONDecodeError as e:
                return {
                    "is_valid": False,
                    "errors": [f"Invalid JSON format: {str(e)}"],
                    "warnings": [],
                    "suggestions": ["Ensure your schema markup is valid JSON format"],
                }

            # Validate structure
            validation_result = self._comprehensive_schema_validation(schema_data)

            return validation_result

        except Exception as e:
            return {
                "is_valid": False,
                "errors": [f"Validation failed: {str(e)}"],
                "warnings": [],
                "suggestions": [],
            }

    def extract_schema_from_url(self, url: str) -> Dict[str, Any]:
        """Extract schema markup from a webpage."""
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, "html.parser")

            extracted_schemas = []

            # Extract JSON-LD scripts
            json_ld_scripts = soup.find_all("script", type="application/ld+json")
            for script in json_ld_scripts:
                try:
                    schema_data = json.loads(script.string)
                    extracted_schemas.append(
                        {"type": "JSON-LD", "data": schema_data, "valid": True}
                    )
                except json.JSONDecodeError:
                    extracted_schemas.append(
                        {
                            "type": "JSON-LD",
                            "data": script.string,
                            "valid": False,
                            "error": "Invalid JSON format",
                        }
                    )

            # Extract microdata
            microdata_items = soup.find_all(attrs={"itemscope": True})
            for item in microdata_items:
                microdata_schema = self._extract_microdata(item)
                if microdata_schema:
                    extracted_schemas.append(
                        {"type": "Microdata", "data": microdata_schema, "valid": True}
                    )

            # Extract RDFa (basic detection)
            rdfa_items = soup.find_all(attrs={"typeof": True})
            for item in rdfa_items[:5]:  # Limit to first 5 items
                rdfa_schema = self._extract_rdfa(item)
                if rdfa_schema:
                    extracted_schemas.append(
                        {"type": "RDFa", "data": rdfa_schema, "valid": True}
                    )

            # Analyze the extracted schemas
            analysis = self._analyze_extracted_schemas(extracted_schemas)

            return {
                "schemas_found": len(extracted_schemas),
                "extracted_schemas": extracted_schemas,
                "analysis": analysis,
                "page_title": soup.title.string if soup.title else None,
                "extraction_timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise Exception(f"Schema extraction failed: {str(e)}")

    def _generate_organization(self, data: Dict) -> Dict:
        """Generate Organization schema."""
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": data.get("name", ""),
        }

        if data.get("url"):
            schema["url"] = data["url"]

        if data.get("logo"):
            schema["logo"] = {"@type": "ImageObject", "url": data["logo"]}

        if data.get("description"):
            schema["description"] = data["description"]

        # Contact information
        if data.get("telephone") or data.get("email"):
            contact_point = {"@type": "ContactPoint", "contactType": "customer service"}
            if data.get("telephone"):
                contact_point["telephone"] = data["telephone"]
            if data.get("email"):
                contact_point["email"] = data["email"]
            schema["contactPoint"] = contact_point

        # Address
        if any(
            data.get(field)
            for field in ["street_address", "city", "state", "postal_code", "country"]
        ):
            address = {"@type": "PostalAddress"}
            if data.get("street_address"):
                address["streetAddress"] = data["street_address"]
            if data.get("city"):
                address["addressLocality"] = data["city"]
            if data.get("state"):
                address["addressRegion"] = data["state"]
            if data.get("postal_code"):
                address["postalCode"] = data["postal_code"]
            if data.get("country"):
                address["addressCountry"] = data["country"]
            schema["address"] = address

        # Social media
        if data.get("social_urls"):
            schema["sameAs"] = (
                data["social_urls"].split(",")
                if isinstance(data["social_urls"], str)
                else data["social_urls"]
            )

        return schema

    def _generate_localbusiness(self, data: Dict) -> Dict:
        """Generate LocalBusiness schema."""
        schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": data.get("name", ""),
        }

        # Address (required)
        address = {"@type": "PostalAddress"}
        if data.get("street_address"):
            address["streetAddress"] = data["street_address"]
        if data.get("city"):
            address["addressLocality"] = data["city"]
        if data.get("state"):
            address["addressRegion"] = data["state"]
        if data.get("postal_code"):
            address["postalCode"] = data["postal_code"]
        if data.get("country"):
            address["addressCountry"] = data["country"]
        schema["address"] = address

        # Contact info
        if data.get("telephone"):
            schema["telephone"] = data["telephone"]
        if data.get("url"):
            schema["url"] = data["url"]

        # Business details
        if data.get("description"):
            schema["description"] = data["description"]
        if data.get("price_range"):
            schema["priceRange"] = data["price_range"]

        # Opening hours
        if data.get("opening_hours"):
            schema["openingHours"] = (
                data["opening_hours"].split(",")
                if isinstance(data["opening_hours"], str)
                else data["opening_hours"]
            )

        # Geo location
        if data.get("latitude") and data.get("longitude"):
            schema["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": data["latitude"],
                "longitude": data["longitude"],
            }

        return schema

    def _generate_product(self, data: Dict) -> Dict:
        """Generate Product schema."""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": data.get("name", ""),
        }

        if data.get("description"):
            schema["description"] = data["description"]

        if data.get("image"):
            schema["image"] = data["image"]

        if data.get("brand"):
            schema["brand"] = {"@type": "Brand", "name": data["brand"]}

        if data.get("sku"):
            schema["sku"] = data["sku"]

        if data.get("mpn"):
            schema["mpn"] = data["mpn"]

        # Offers
        if any(data.get(field) for field in ["price", "currency", "availability"]):
            offer = {"@type": "Offer", "priceCurrency": data.get("currency", "USD")}
            if data.get("price"):
                offer["price"] = data["price"]
            if data.get("availability"):
                availability_map = {
                    "in_stock": "https://schema.org/InStock",
                    "out_of_stock": "https://schema.org/OutOfStock",
                    "limited_availability": "https://schema.org/LimitedAvailability",
                }
                offer["availability"] = availability_map.get(
                    data["availability"], "https://schema.org/InStock"
                )
            if data.get("url"):
                offer["url"] = data["url"]
            schema["offers"] = offer

        return schema

    def _generate_article(self, data: Dict) -> Dict:
        """Generate Article schema."""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": data.get("headline", ""),
            "datePublished": data.get("date_published", datetime.utcnow().isoformat()),
        }

        # Author
        if data.get("author_name"):
            schema["author"] = {"@type": "Person", "name": data["author_name"]}
            if data.get("author_url"):
                schema["author"]["url"] = data["author_url"]

        # Publisher
        if data.get("publisher_name"):
            publisher = {"@type": "Organization", "name": data["publisher_name"]}
            if data.get("publisher_logo"):
                publisher["logo"] = {
                    "@type": "ImageObject",
                    "url": data["publisher_logo"],
                }
            schema["publisher"] = publisher

        if data.get("description"):
            schema["description"] = data["description"]

        if data.get("image"):
            schema["image"] = data["image"]

        if data.get("date_modified"):
            schema["dateModified"] = data["date_modified"]

        if data.get("url"):
            schema["mainEntityOfPage"] = {"@type": "WebPage", "@id": data["url"]}

        return schema

    def _generate_event(self, data: Dict) -> Dict:
        """Generate Event schema."""
        schema = {
            "@context": "https://schema.org",
            "@type": "Event",
            "name": data.get("name", ""),
            "startDate": data.get("start_date", ""),
        }

        if data.get("end_date"):
            schema["endDate"] = data["end_date"]

        if data.get("description"):
            schema["description"] = data["description"]

        # Location
        if data.get("location_name") or data.get("address"):
            location = {"@type": "Place"}
            if data.get("location_name"):
                location["name"] = data["location_name"]
            if data.get("address"):
                location["address"] = data["address"]
            schema["location"] = location

        # Organizer
        if data.get("organizer_name"):
            schema["organizer"] = {
                "@type": "Organization",
                "name": data["organizer_name"],
            }
            if data.get("organizer_url"):
                schema["organizer"]["url"] = data["organizer_url"]

        # Offers/Tickets
        if data.get("ticket_price") or data.get("ticket_url"):
            offer = {
                "@type": "Offer",
                "price": data.get("ticket_price", "0"),
                "priceCurrency": data.get("currency", "USD"),
            }
            if data.get("ticket_url"):
                offer["url"] = data["ticket_url"]
            schema["offers"] = offer

        return schema

    def _generate_generic_schema(self, schema_type: str, data: Dict) -> Dict:
        """Generate a generic schema for unsupported types."""
        schema = {"@context": "https://schema.org", "@type": schema_type}

        # Add common properties
        for key, value in data.items():
            if value and key not in ["schema_type"]:
                # Convert snake_case to camelCase
                camel_key = self._to_camel_case(key)
                schema[camel_key] = value

        return schema

    def _validate_schema_structure(self, schema: Dict, schema_type: str) -> Dict:
        """Validate schema structure against requirements."""
        template = self.schema_templates.get(schema_type, {})
        errors = []
        warnings = []
        suggestions = []

        # Check required properties
        required_props = template.get("required", [])
        for prop in required_props:
            if prop not in schema or not schema[prop]:
                errors.append(f"Missing required property: {prop}")

        # Check recommended properties
        recommended_props = template.get("recommended", [])
        for prop in recommended_props:
            if prop not in schema or not schema[prop]:
                warnings.append(f"Missing recommended property: {prop}")
                suggestions.append(f"Consider adding '{prop}' for better SEO")

        # Validate @context and @type
        if "@context" not in schema:
            errors.append("Missing @context property")
        elif schema["@context"] != "https://schema.org":
            warnings.append("Consider using 'https://schema.org' for @context")

        if "@type" not in schema:
            errors.append("Missing @type property")
        elif schema["@type"] != schema_type:
            warnings.append(
                f"@type mismatch: expected {schema_type}, got {schema['@type']}"
            )

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "completeness_score": self._calculate_completeness_score(schema, template),
        }

    def _comprehensive_schema_validation(self, schema_data: Dict) -> Dict:
        """Comprehensive validation of schema markup."""
        errors = []
        warnings = []
        suggestions = []

        # Handle arrays of schemas
        schemas_to_validate = (
            schema_data if isinstance(schema_data, list) else [schema_data]
        )

        for schema in schemas_to_validate:
            if not isinstance(schema, dict):
                errors.append("Schema must be a JSON object")
                continue

            # Validate basic structure
            if "@type" not in schema:
                errors.append("Missing @type property")
                continue

            schema_type = schema.get("@type")
            if schema_type in self.schema_templates:
                validation = self._validate_schema_structure(schema, schema_type)
                errors.extend(validation["errors"])
                warnings.extend(validation["warnings"])
                suggestions.extend(validation["suggestions"])
            else:
                warnings.append(f"Unknown schema type: {schema_type}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "schemas_validated": len(schemas_to_validate),
        }

    def _format_json_ld(self, schema: Dict) -> str:
        """Format schema as JSON-LD for HTML embedding."""
        json_ld = json.dumps(schema, indent=2, ensure_ascii=False)
        return f'<script type="application/ld+json">\n{json_ld}\n</script>'

    def _generate_microdata_example(self, schema: Dict, schema_type: str) -> str:
        """Generate microdata example for the schema."""
        if schema_type == "Organization":
            return self._microdata_organization_example(schema)
        elif schema_type == "LocalBusiness":
            return self._microdata_business_example(schema)
        elif schema_type == "Product":
            return self._microdata_product_example(schema)
        else:
            return self._microdata_generic_example(schema, schema_type)

    def _microdata_organization_example(self, schema: Dict) -> str:
        """Generate microdata example for Organization."""
        return f"""<div itemscope itemtype="https://schema.org/Organization">
    <span itemprop="name">{schema.get('name', 'Your Organization Name')}</span>
    {f'<meta itemprop="url" content="{schema.get("url")}">' if schema.get('url') else ''}
    {f'<img itemprop="logo" src="{schema.get("logo", {}).get("url")}" alt="Logo">' if schema.get('logo') else ''}
    {f'<meta itemprop="description" content="{schema.get("description")}">' if schema.get('description') else ''}
</div>"""

    def _microdata_business_example(self, schema: Dict) -> str:
        """Generate microdata example for LocalBusiness."""
        address = schema.get("address", {})
        return f"""<div itemscope itemtype="https://schema.org/LocalBusiness">
    <span itemprop="name">{schema.get('name', 'Your Business Name')}</span>
    <div itemprop="address" itemscope itemtype="https://schema.org/PostalAddress">
        <span itemprop="streetAddress">{address.get('streetAddress', 'Street Address')}</span>
        <span itemprop="addressLocality">{address.get('addressLocality', 'City')}</span>
        <span itemprop="addressRegion">{address.get('addressRegion', 'State')}</span>
    </div>
    {f'<span itemprop="telephone">{schema.get("telephone")}</span>' if schema.get('telephone') else ''}
</div>"""

    def _microdata_product_example(self, schema: Dict) -> str:
        """Generate microdata example for Product."""
        offers = schema.get("offers", {})
        return f"""<div itemscope itemtype="https://schema.org/Product">
    <span itemprop="name">{schema.get('name', 'Product Name')}</span>
    {f'<meta itemprop="description" content="{schema.get("description")}">' if schema.get('description') else ''}
    <div itemprop="offers" itemscope itemtype="https://schema.org/Offer">
        <span itemprop="price">{offers.get('price', '0')}</span>
        <meta itemprop="priceCurrency" content="{offers.get('priceCurrency', 'USD')}">
    </div>
</div>"""

    def _microdata_generic_example(self, schema: Dict, schema_type: str) -> str:
        """Generate generic microdata example."""
        return f"""<div itemscope itemtype="https://schema.org/{schema_type}">
    <!-- Add your content with itemprop attributes -->
    <span itemprop="name">{schema.get('name', 'Name')}</span>
    {f'<meta itemprop="description" content="{schema.get("description")}">' if schema.get('description') else ''}
</div>"""

    def _extract_microdata(self, element) -> Optional[Dict]:
        """Extract microdata from an element."""
        try:
            schema = {}

            # Get item type
            item_type = element.get("itemtype")
            if item_type:
                schema["@type"] = item_type.split("/")[-1]
                schema["@context"] = "https://schema.org"

            # Extract properties
            props = element.find_all(attrs={"itemprop": True})
            for prop in props:
                prop_name = prop.get("itemprop")
                prop_value = self._extract_microdata_value(prop)
                if prop_value:
                    schema[prop_name] = prop_value

            return (
                schema if len(schema) > 2 else None
            )  # Must have more than just @type and @context

        except Exception:
            return None

    def _extract_microdata_value(self, element):
        """Extract value from microdata element."""
        # Check for meta content
        if element.name == "meta":
            return element.get("content")

        # Check for common value attributes
        for attr in ["content", "datetime", "href", "src"]:
            if element.has_attr(attr):
                return element[attr]

        # Return text content
        return element.get_text(strip=True)

    def _extract_rdfa(self, element) -> Optional[Dict]:
        """Extract RDFa from an element."""
        try:
            schema = {}

            # Get type
            typeof = element.get("typeof")
            if typeof:
                schema["@type"] = typeof
                schema["@context"] = "https://schema.org"

            # Extract properties (simplified)
            props = element.find_all(attrs={"property": True})
            for prop in props[:5]:  # Limit to avoid excessive processing
                prop_name = prop.get("property")
                prop_value = prop.get("content") or prop.get_text(strip=True)
                if prop_value:
                    schema[prop_name] = prop_value

            return schema if len(schema) > 2 else None

        except Exception:
            return None

    def _analyze_extracted_schemas(self, schemas: List[Dict]) -> Dict:
        """Analyze extracted schemas for insights."""
        analysis = {
            "total_schemas": len(schemas),
            "schema_types": [],
            "formats_found": set(),
            "valid_schemas": 0,
            "invalid_schemas": 0,
            "recommendations": [],
        }

        for schema_info in schemas:
            analysis["formats_found"].add(schema_info["type"])

            if schema_info.get("valid", False):
                analysis["valid_schemas"] += 1

                # Extract schema type
                schema_data = schema_info.get("data", {})
                if isinstance(schema_data, dict):
                    schema_type = schema_data.get("@type")
                    if schema_type and schema_type not in analysis["schema_types"]:
                        analysis["schema_types"].append(schema_type)
            else:
                analysis["invalid_schemas"] += 1

        # Convert set to list for JSON serialization
        analysis["formats_found"] = list(analysis["formats_found"])

        # Generate recommendations
        if analysis["invalid_schemas"] > 0:
            analysis["recommendations"].append(
                "Fix invalid schema markup for better SEO"
            )

        if "JSON-LD" not in analysis["formats_found"] and analysis["total_schemas"] > 0:
            analysis["recommendations"].append(
                "Consider using JSON-LD format for easier maintenance"
            )

        if analysis["total_schemas"] == 0:
            analysis["recommendations"].append(
                "Add structured data markup to improve SEO"
            )

        return analysis

    def _calculate_completeness_score(self, schema: Dict, template: Dict) -> int:
        """Calculate completeness score based on required and recommended properties."""
        required_props = template.get("required", [])
        recommended_props = template.get("recommended", [])

        total_possible = len(required_props) + len(recommended_props)
        if total_possible == 0:
            return 100

        score = 0

        # Required properties are worth more
        for prop in required_props:
            if prop in schema and schema[prop]:
                score += 70 / len(required_props) if required_props else 0

        # Recommended properties
        for prop in recommended_props:
            if prop in schema and schema[prop]:
                score += 30 / len(recommended_props) if recommended_props else 0

        return min(100, round(score))

    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase."""
        components = snake_str.split("_")
        return components[0] + "".join(word.capitalize() for word in components[1:])
