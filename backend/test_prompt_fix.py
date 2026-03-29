"""
Test Prompt Engineering Fix
============================
Test the improved virtual try-on prompt with:
- 3 problematic products (shirt-002, dress-001, kurta-002)
- 3 random products for comparison
"""

import asyncio
import os
import json
import sys
import random
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from app.services.gemini_service import gemini_service
from app.config import settings


async def test_prompt_fix():
    """Test the improved prompt with specific products"""

    # Paths
    project_root = Path(__file__).parent.parent
    input_image = project_root / "archive" / "input.png"
    products_json = project_root / "backend" / "data" / "products.json"
    products_dir = project_root / "frontend" / "public" / "products"

    # Create results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = project_root / "experiment_results" / f"prompt_fix_test_{timestamp}"
    results_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*60)
    print("  PROMPT ENGINEERING FIX TEST")
    print("="*60 + "\n")
    print(f"📸 Input image: {input_image}")
    print(f"💾 Results: {results_dir}")
    print("-" * 60)

    # Load all products
    with open(products_json, 'r') as f:
        all_products = json.load(f)

    # Problematic products (MUST test these)
    problematic_ids = ["shirt-002", "dress-001", "kurta-002"]

    # Get the problematic products
    problematic_products = [p for p in all_products if p['id'] in problematic_ids]

    # Get 3 random products from the rest
    other_products = [p for p in all_products if p['id'] not in problematic_ids]
    random_products = random.sample(other_products, min(3, len(other_products)))

    # Combine for testing
    test_products = problematic_products + random_products

    print(f"\n🎯 Testing {len(test_products)} products:\n")
    print("PROBLEMATIC (must fix):")
    for p in problematic_products:
        print(f"  - {p['name']} ({p['id']})")

    print("\nRANDOM COMPARISON:")
    for p in random_products:
        print(f"  - {p['name']} ({p['id']})")

    print("\n" + "-" * 60 + "\n")

    # Results tracking
    results = []
    successful = 0
    failed = 0

    # Process each product
    for idx, product in enumerate(test_products, 1):
        product_id = product['id']
        product_name = product['name']
        category = product['category']
        is_problematic = product_id in problematic_ids

        status_marker = "🔴" if is_problematic else "🔵"
        print(f"{status_marker} [{idx}/{len(test_products)}] {product_name} ({product_id})")

        # Map product ID to garment image
        product_parts = product_id.rsplit('-', 1)
        if len(product_parts) == 2:
            category_part = product_parts[0]
            number = product_parts[1].lstrip('0') or '1'
            garment_filename = f"{category_part}-{number}.jpg"
        else:
            garment_filename = f"{product_id}.jpg"

        garment_image_path = products_dir / garment_filename

        if not garment_image_path.exists():
            print(f"  ⚠️  Garment image not found: {garment_filename}\n")
            results.append({
                "product_id": product_id,
                "product_name": product_name,
                "is_problematic": is_problematic,
                "status": "error",
                "error": "Garment image not found"
            })
            failed += 1
            continue

        try:
            # Generate try-on with NEW improved prompt
            result = await gemini_service.generate_tryon(
                person_image_path=str(input_image),
                garment_image_path=str(garment_image_path),
                custom_prompt=None
            )

            if result["status"] == "success":
                # Copy result to organized directory
                import shutil
                source_path = result["image_path"]

                problem_prefix = "FIXED_" if is_problematic else ""
                dest_filename = f"{idx:02d}_{problem_prefix}{product_id}_{category}.jpg"
                dest_path = results_dir / dest_filename

                shutil.copy2(source_path, dest_path)

                print(f"  ✅ Success! Saved as: {dest_filename}\n")

                results.append({
                    "product_id": product_id,
                    "product_name": product_name,
                    "category": category,
                    "is_problematic": is_problematic,
                    "status": "success",
                    "output_file": dest_filename
                })
                successful += 1

            else:
                print(f"  ❌ Failed: {result.get('message', 'Unknown error')}\n")
                results.append({
                    "product_id": product_id,
                    "product_name": product_name,
                    "is_problematic": is_problematic,
                    "status": "error",
                    "error": result.get('message', 'Unknown error')
                })
                failed += 1

        except Exception as e:
            print(f"  ❌ Exception: {str(e)}\n")
            results.append({
                "product_id": product_id,
                "product_name": product_name,
                "is_problematic": is_problematic,
                "status": "error",
                "error": str(e)
            })
            failed += 1

    # Save results summary
    summary = {
        "test": "Prompt Engineering Fix Verification",
        "timestamp": timestamp,
        "input_image": str(input_image),
        "total_tested": len(test_products),
        "problematic_products": problematic_ids,
        "successful": successful,
        "failed": failed,
        "results": results
    }

    summary_path = results_dir / "test_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    # Print final summary
    print("=" * 60)
    print("🎉 Test Complete!")
    print(f"✅ Successful: {successful}/{len(test_products)}")
    print(f"❌ Failed: {failed}/{len(test_products)}")

    # Check if problematic ones are fixed
    problematic_results = [r for r in results if r.get('is_problematic')]
    problematic_fixed = sum(1 for r in problematic_results if r['status'] == 'success')

    print(f"\n🎯 PROBLEMATIC PRODUCTS:")
    print(f"   Fixed: {problematic_fixed}/{len(problematic_results)}")

    print(f"\n📁 Results: {results_dir}")
    print(f"📄 Summary: test_summary.json")
    print("=" * 60)

    # Create comparison HTML
    create_comparison_html(results_dir, summary, str(input_image.relative_to(project_root)))


def create_comparison_html(results_dir: Path, summary: dict, input_image_rel: str):
    """Create HTML viewer with focus on problematic products"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Fix Test - {summary['timestamp']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
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
        h1 {{ color: #333; margin-bottom: 10px; }}
        .summary {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .stat {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #2196f3;
        }}
        .stat.problematic {{
            border-left-color: #f44336;
        }}
        .stat-label {{
            font-size: 13px;
            color: #666;
            margin-bottom: 5px;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: 600;
            color: #333;
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
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            margin: 40px 0 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .section-title.problematic {{
            color: #f44336;
        }}
        .results-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
        }}
        .result-card {{
            border: 2px solid #e0e0e0;
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
        .result-card.problematic {{
            border-color: #f44336;
            background: #fff5f5;
        }}
        .result-card.problematic.success {{
            border-color: #ff9800;
            background: #fff8e1;
        }}
        .result-image {{
            width: 100%;
            height: 380px;
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
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            margin: 5px 5px 0 0;
        }}
        .badge.problematic {{
            background: #ffebee;
            color: #c62828;
        }}
        .badge.fixed {{
            background: #fff3e0;
            color: #e65100;
        }}
        .badge.success {{
            background: #e8f5e9;
            color: #2e7d32;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Prompt Engineering Fix - Test Results</h1>
        <p style="color: #666; margin-top: 10px;">Generated on {summary['timestamp']}</p>

        <div class="summary">
            <h2 style="margin-bottom: 15px;">Test Summary</h2>
            <div class="stats">
                <div class="stat">
                    <div class="stat-label">Total Tested</div>
                    <div class="stat-value">{summary['total_tested']}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Successful</div>
                    <div class="stat-value" style="color: #4caf50;">{summary['successful']}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Failed</div>
                    <div class="stat-value" style="color: #f44336;">{summary['failed']}</div>
                </div>
                <div class="stat problematic">
                    <div class="stat-label">Problematic Fixed</div>
                    <div class="stat-value" style="color: #ff9800;">{sum(1 for r in summary['results'] if r.get('is_problematic') and r['status'] == 'success')}/{len([r for r in summary['results'] if r.get('is_problematic')])}</div>
                </div>
            </div>
        </div>

        <div class="input-section">
            <h3 style="margin-bottom: 15px;">Input Image</h3>
            <img src="../../{input_image_rel}" alt="Input" class="input-image">
        </div>
"""

    # Separate problematic and regular results
    problematic_results = [r for r in summary['results'] if r.get('is_problematic')]
    regular_results = [r for r in summary['results'] if not r.get('is_problematic')]

    # Problematic products section
    if problematic_results:
        html_content += """
        <h2 class="section-title problematic">🔴 Previously Problematic Products (Testing Fix)</h2>
        <div class="results-grid">
"""
        for result in problematic_results:
            if result['status'] == 'success':
                html_content += f"""
            <div class="result-card problematic success">
                <img src="{result['output_file']}" alt="{result['product_name']}" class="result-image">
                <div class="result-info">
                    <div class="result-title">{result['product_name']}</div>
                    <div class="result-meta">ID: {result['product_id']}</div>
                    <div class="result-meta">Category: {result['category']}</div>
                    <span class="badge problematic">WAS PROBLEMATIC</span>
                    <span class="badge fixed">✓ FIXED</span>
                </div>
            </div>
"""
        html_content += """
        </div>
"""

    # Regular products section
    if regular_results:
        html_content += """
        <h2 class="section-title">🔵 Comparison Products (Random Selection)</h2>
        <div class="results-grid">
"""
        for result in regular_results:
            if result['status'] == 'success':
                html_content += f"""
            <div class="result-card success">
                <img src="{result['output_file']}" alt="{result['product_name']}" class="result-image">
                <div class="result-info">
                    <div class="result-title">{result['product_name']}</div>
                    <div class="result-meta">ID: {result['product_id']}</div>
                    <div class="result-meta">Category: {result['category']}</div>
                    <span class="badge success">✓ Success</span>
                </div>
            </div>
"""
        html_content += """
        </div>
"""

    html_content += """
    </div>
</body>
</html>
"""

    viewer_path = results_dir / "test_results.html"
    with open(viewer_path, 'w') as f:
        f.write(html_content)

    print(f"🌐 Test viewer created: test_results.html")
    print(f"   file://{viewer_path}")


if __name__ == "__main__":
    asyncio.run(test_prompt_fix())
