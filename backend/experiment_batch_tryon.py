"""
Experiment: Batch Virtual Try-On
================================
Test try-on capability with all 12 products against a single input image.
Results saved for manual review.
"""

import asyncio
import os
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.services.gemini_service import gemini_service
from app.config import settings


async def batch_tryon_experiment():
    """Run try-on experiment with all products"""

    # Paths
    project_root = Path(__file__).parent.parent
    input_image = project_root / "archive" / "input.png"
    products_json = project_root / "backend" / "data" / "products.json"
    products_dir = project_root / "frontend" / "public" / "products"

    # Create results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = project_root / "experiment_results" / f"batch_tryon_{timestamp}"
    results_dir.mkdir(parents=True, exist_ok=True)

    print(f"🧪 Starting Batch Try-On Experiment")
    print(f"📸 Input image: {input_image}")
    print(f"💾 Results will be saved to: {results_dir}")
    print("-" * 60)

    # Load products
    with open(products_json, 'r') as f:
        products = json.load(f)

    print(f"📦 Found {len(products)} products to test\n")

    # Results tracking
    results = []
    successful = 0
    failed = 0

    # Process each product
    for idx, product in enumerate(products, 1):
        product_id = product['id']
        product_name = product['name']
        category = product['category']

        print(f"[{idx}/{len(products)}] Processing: {product_name} ({product_id})")

        # Map product ID to garment image filename
        # e.g., "shirt-001" -> "shirt-1.jpg"
        product_parts = product_id.rsplit('-', 1)
        if len(product_parts) == 2:
            category_part = product_parts[0]
            number = product_parts[1].lstrip('0') or '1'
            garment_filename = f"{category_part}-{number}.jpg"
        else:
            garment_filename = f"{product_id}.jpg"

        garment_image_path = products_dir / garment_filename

        if not garment_image_path.exists():
            print(f"  ⚠️  Garment image not found: {garment_filename}")
            results.append({
                "product_id": product_id,
                "product_name": product_name,
                "status": "error",
                "error": "Garment image not found"
            })
            failed += 1
            continue

        try:
            # Generate try-on
            result = await gemini_service.generate_tryon(
                person_image_path=str(input_image),
                garment_image_path=str(garment_image_path),
                custom_prompt=None
            )

            if result["status"] == "success":
                # Copy result to our organized directory with descriptive name
                source_path = result["image_path"]
                dest_filename = f"{idx:02d}_{product_id}_{category}.jpg"
                dest_path = results_dir / dest_filename

                # Copy the generated image
                import shutil
                shutil.copy2(source_path, dest_path)

                print(f"  ✅ Success! Saved as: {dest_filename}")

                results.append({
                    "product_id": product_id,
                    "product_name": product_name,
                    "category": category,
                    "status": "success",
                    "output_file": dest_filename
                })
                successful += 1

            else:
                print(f"  ❌ Failed: {result.get('message', 'Unknown error')}")
                results.append({
                    "product_id": product_id,
                    "product_name": product_name,
                    "status": "error",
                    "error": result.get('message', 'Unknown error')
                })
                failed += 1

        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            results.append({
                "product_id": product_id,
                "product_name": product_name,
                "status": "error",
                "error": str(e)
            })
            failed += 1

        print()

    # Save results summary
    summary = {
        "experiment": "Batch Virtual Try-On",
        "timestamp": timestamp,
        "input_image": str(input_image),
        "total_products": len(products),
        "successful": successful,
        "failed": failed,
        "results": results
    }

    summary_path = results_dir / "summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    # Print final summary
    print("=" * 60)
    print(f"🎉 Experiment Complete!")
    print(f"✅ Successful: {successful}/{len(products)}")
    print(f"❌ Failed: {failed}/{len(products)}")
    print(f"📁 Results directory: {results_dir}")
    print(f"📄 Summary saved to: summary.json")
    print("=" * 60)

    # Create a simple HTML viewer for easy review
    create_html_viewer(results_dir, summary, str(input_image.relative_to(project_root)))


def create_html_viewer(results_dir: Path, summary: dict, input_image_rel: str):
    """Create an HTML file to easily view all results"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Try-On Experiment Results - {summary['timestamp']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .summary {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .summary-stats {{
            display: flex;
            gap: 30px;
            margin-top: 15px;
        }}
        .stat {{
            font-size: 16px;
        }}
        .stat strong {{
            color: #666;
        }}
        .input-section {{
            margin: 30px 0;
            text-align: center;
        }}
        .input-image {{
            max-width: 300px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        .results-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}
        .result-card {{
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .result-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .result-card.success {{
            border-color: #4caf50;
        }}
        .result-card.error {{
            border-color: #f44336;
            background: #fff5f5;
        }}
        .result-image {{
            width: 100%;
            height: 350px;
            object-fit: cover;
            background: #fafafa;
        }}
        .result-info {{
            padding: 15px;
        }}
        .result-title {{
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }}
        .result-meta {{
            font-size: 13px;
            color: #666;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 8px;
        }}
        .status-badge.success {{
            background: #e8f5e9;
            color: #2e7d32;
        }}
        .status-badge.error {{
            background: #ffebee;
            color: #c62828;
        }}
        .error-message {{
            font-size: 12px;
            color: #d32f2f;
            margin-top: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Virtual Try-On Experiment Results</h1>
        <p style="color: #666; margin-top: 10px;">Generated on {summary['timestamp']}</p>

        <div class="summary">
            <h2 style="margin-bottom: 15px;">Experiment Summary</h2>
            <div class="summary-stats">
                <div class="stat">
                    <strong>Total Products:</strong> {summary['total_products']}
                </div>
                <div class="stat">
                    <strong>Successful:</strong> <span style="color: #4caf50;">{summary['successful']}</span>
                </div>
                <div class="stat">
                    <strong>Failed:</strong> <span style="color: #f44336;">{summary['failed']}</span>
                </div>
                <div class="stat">
                    <strong>Success Rate:</strong> {round(summary['successful']/summary['total_products']*100, 1)}%
                </div>
            </div>
        </div>

        <div class="input-section">
            <h3 style="margin-bottom: 15px;">Input Image</h3>
            <img src="../../{input_image_rel}" alt="Input" class="input-image">
        </div>

        <h2 style="margin: 40px 0 20px;">Generated Try-Ons</h2>
        <div class="results-grid">
"""

    for result in summary['results']:
        status_class = result['status']

        if result['status'] == 'success':
            html_content += f"""
            <div class="result-card success">
                <img src="{result['output_file']}" alt="{result['product_name']}" class="result-image">
                <div class="result-info">
                    <div class="result-title">{result['product_name']}</div>
                    <div class="result-meta">ID: {result['product_id']}</div>
                    <div class="result-meta">Category: {result['category']}</div>
                    <span class="status-badge success">✓ Success</span>
                </div>
            </div>
"""
        else:
            html_content += f"""
            <div class="result-card error">
                <div style="height: 350px; display: flex; align-items: center; justify-content: center; background: #fafafa; color: #999;">
                    <div style="text-align: center;">
                        <div style="font-size: 48px; margin-bottom: 10px;">❌</div>
                        <div>Failed to generate</div>
                    </div>
                </div>
                <div class="result-info">
                    <div class="result-title">{result['product_name']}</div>
                    <div class="result-meta">ID: {result['product_id']}</div>
                    <span class="status-badge error">✗ Failed</span>
                    <div class="error-message">{result.get('error', 'Unknown error')}</div>
                </div>
            </div>
"""

    html_content += """
        </div>
    </div>
</body>
</html>
"""

    viewer_path = results_dir / "viewer.html"
    with open(viewer_path, 'w') as f:
        f.write(html_content)

    print(f"🌐 HTML viewer created: viewer.html")
    print(f"   Open in browser to view results: file://{viewer_path}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  BATCH VIRTUAL TRY-ON EXPERIMENT")
    print("="*60 + "\n")

    # Run the experiment
    asyncio.run(batch_tryon_experiment())
