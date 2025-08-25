"""
🎯 Kép Lệch Performance Analysis - Management Command
====================================================
Django management command để chạy phân tích Kép Lệch từ command line
"""

import json
from datetime import datetime

from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from predictions_tracker.kep_lech_performance_analyzer import (
    kep_lech_performance_analyzer,
)
from results.models import KetQuaXoSo


class Command(BaseCommand):
    help = "🎯 Run Kép Lệch Performance Analysis"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=730,
            help="Number of days to analyze (default: 730 = 2 years)",
        )

        parser.add_argument(
            "--output-file",
            type=str,
            help="Output file path to save analysis results (JSON format)",
        )

        parser.add_argument(
            "--format",
            type=str,
            choices=["full", "summary", "simple"],
            default="full",
            help="Output format (default: full)",
        )

        parser.add_argument(
            "--clear-cache",
            action="store_true",
            help="Clear cache before running analysis",
        )

        parser.add_argument(
            "--verbose", action="store_true", help="Enable verbose output"
        )

    def handle(self, *args, **options):
        """Main command handler"""
        start_time = timezone.now()

        try:
            self.stdout.write(
                self.style.SUCCESS("🎯 Starting Kép Lệch Performance Analysis...")
            )

            # Get options
            days = options["days"]
            output_file = options.get("output_file")
            format_type = options["format"]
            clear_cache = options["clear_cache"]
            verbose = options["verbose"]

            # Check data availability first
            total_results = KetQuaXoSo.objects.count()
            if total_results == 0:
                raise CommandError("❌ No lottery results data available for analysis")

            if verbose:
                earliest = KetQuaXoSo.objects.earliest("ngay")
                latest = KetQuaXoSo.objects.latest("ngay")
                self.stdout.write(f"📊 Data range: {earliest.ngay} to {latest.ngay}")
                self.stdout.write(f"📊 Total results: {total_results}")
                self.stdout.write(f"📊 Analysis period: {days} days")

            # Clear cache if requested
            if clear_cache:
                self.stdout.write("🗑️ Clearing cache...")
                cache_key = f"kep_lech_analysis_{days}"
                cache.delete(cache_key)
                if verbose:
                    self.stdout.write("✅ Cache cleared")

            # Run analysis
            self.stdout.write(f"🔍 Running analysis for {days} days...")
            analysis_result = kep_lech_performance_analyzer.run_complete_analysis(days)

            if not analysis_result.get("success", False):
                raise CommandError(
                    f'❌ Analysis failed: {analysis_result.get("error", "Unknown error")}'
                )

            # Process results based on format
            if format_type == "simple":
                output_data = self._create_simple_summary(analysis_result)
            elif format_type == "summary":
                output_data = self._create_summary_format(analysis_result)
            else:  # full
                output_data = analysis_result

            # Display results
            self._display_results(output_data, verbose)

            # Save to file if requested
            if output_file:
                self._save_to_file(output_data, output_file)
                self.stdout.write(
                    self.style.SUCCESS(f"💾 Results saved to: {output_file}")
                )

            # Execution time
            end_time = timezone.now()
            execution_time = (end_time - start_time).total_seconds()

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Analysis completed in {execution_time:.2f} seconds"
                )
            )

        except Exception as e:
            raise CommandError(f"❌ Command failed: {str(e)}")

    def _create_simple_summary(self, analysis_result):
        """Create simple summary format"""
        summary = analysis_result.get("summary_statistics", {})

        return {
            "analysis_date": datetime.now().isoformat(),
            "period_days": analysis_result.get("analysis_metadata", {})
            .get("analysis_period", {})
            .get("total_days", 0),
            "weeks_analyzed": summary.get("total_weeks_analyzed", 0),
            "success_rate_percent": round(
                summary.get("prediction_accuracy", {}).get("success_rate", 0), 1
            ),
            "total_roi_percent": round(
                summary.get("financial_performance", {}).get("total_roi", 0), 1
            ),
            "risk_level": summary.get("risk_assessment", {}).get(
                "risk_level", "unknown"
            ),
            "recommendation": analysis_result.get("strategy_recommendations", {}).get(
                "overall_verdict", "unknown"
            ),
            "winning_weeks": summary.get("financial_performance", {}).get(
                "winning_weeks", 0
            ),
            "losing_weeks": summary.get("financial_performance", {}).get(
                "losing_weeks", 0
            ),
            "net_profit_vnd": summary.get("financial_performance", {}).get(
                "total_profit", 0
            ),
        }

    def _create_summary_format(self, analysis_result):
        """Create summary format"""
        return {
            "metadata": analysis_result.get("analysis_metadata", {}),
            "summary_statistics": analysis_result.get("summary_statistics", {}),
            "strategy_recommendations": analysis_result.get(
                "strategy_recommendations", {}
            ),
            "risk_analysis_summary": {
                "risk_level": analysis_result.get("risk_analysis", {}).get(
                    "risk_level", "unknown"
                ),
                "capital_requirements": analysis_result.get("risk_analysis", {}).get(
                    "capital_requirements", {}
                ),
                "scenario_analysis": analysis_result.get("risk_analysis", {}).get(
                    "scenario_analysis", {}
                ),
            },
        }

    def _display_results(self, data, verbose=False):
        """Display analysis results"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS("📊 KÉP LỆCH PERFORMANCE ANALYSIS RESULTS")
        )
        self.stdout.write("=" * 60)

        if "success_rate_percent" in data:  # Simple format
            self.stdout.write(f'🎯 Success Rate: {data["success_rate_percent"]}%')
            self.stdout.write(f'💰 Total ROI: {data["total_roi_percent"]}%')
            self.stdout.write(f'⚠️ Risk Level: {data["risk_level"].title()}')
            self.stdout.write(
                f'💡 Recommendation: {data["recommendation"].replace("_", " ").title()}'
            )
            self.stdout.write(
                f'📈 Winning/Losing Weeks: {data["winning_weeks"]}/{data["losing_weeks"]}'
            )
            self.stdout.write(f'💵 Net Profit: {data["net_profit_vnd"]:,.0f} VND')

        elif "summary_statistics" in data:  # Summary or full format
            summary = data.get("summary_statistics", {})

            self.stdout.write(
                f'📅 Weeks Analyzed: {summary.get("total_weeks_analyzed", 0)}'
            )
            self.stdout.write(
                f'🎯 Success Rate: {summary.get("prediction_accuracy", {}).get("success_rate", 0):.1f}%'
            )
            self.stdout.write(
                f'💰 Total ROI: {summary.get("financial_performance", {}).get("total_roi", 0):.1f}%'
            )
            self.stdout.write(
                f'⚠️ Risk Level: {summary.get("risk_assessment", {}).get("risk_level", "unknown").title()}'
            )

            if verbose and "strategy_recommendations" in data:
                recommendations = data["strategy_recommendations"]
                self.stdout.write("\n📋 KEY RECOMMENDATIONS:")

                for strategy in recommendations.get("investment_strategy", [])[:3]:
                    self.stdout.write(f"  • {strategy}")

                for risk_tip in recommendations.get("risk_management", [])[:2]:
                    self.stdout.write(f"  • {risk_tip}")

        self.stdout.write("=" * 60 + "\n")

    def _save_to_file(self, data, filepath):
        """Save results to JSON file"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            raise CommandError(f"Failed to save file: {str(e)}")
