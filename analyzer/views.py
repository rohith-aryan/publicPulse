from django.shortcuts import render
from .models import ReviewAnalysis
from .helper import analyze_url

def analyze_feedback(request):
    if request.method == 'POST':
        url = request.POST.get('url')

        existing_data = ReviewAnalysis.objects.filter(url=url).first()
        if existing_data:
            return render(request, 'analyzer/index.html', {
                'verdict': existing_data.final_verdict,
                'overall_rating': existing_data.overall_rating,
                'ratings': existing_data.rating_percentages,
                'top_reviews': existing_data.top_reviews,
                'keywords': existing_data.keywords
            })


        analysis_data = analyze_url(url)

        # Debug print to check returned data
        print("Analysis Result:", analysis_data)

        verdict = analysis_data.get('final_verdict')
        rating = analysis_data.get('overall_rating')
        ratings_breakdown = analysis_data.get('ratings')
        top_reviews = analysis_data.get('top_reviews')
        keywords = analysis_data.get('keywords')

        # Check if required fields are present
        if verdict and rating is not None:
            saved_data = ReviewAnalysis.objects.create(
                url=url,
                final_verdict=verdict,
                overall_rating=rating,
                rating_percentages=ratings_breakdown or {},
                top_reviews=top_reviews or [],
                keywords=keywords or []
            )
            return render(request, 'analyzer/index.html', {
                'verdict': verdict,
                'overall_rating': rating,
                'ratings': ratings_breakdown,
                'top_reviews': top_reviews,
                'keywords': keywords
            })

        else:
            error_msg = "Failed to analyze feedback. Please try a different URL."
            return render(request, 'analyzer/index.html', {'error': error_msg})

    return render(request, 'analyzer/index.html')
