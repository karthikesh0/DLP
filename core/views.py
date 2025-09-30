import os
from django.shortcuts import render
from django.conf import settings
from predict import predict_single_image  # make sure this matches your utils file

def home(request):
    verdict = None
    image_url = None
    error = None
    classification = None  # Default in case not set

    if request.method == 'POST':
        root_dir = os.path.dirname(os.path.abspath(__file__))
        uploaded_file = request.FILES.get('image')
        print(uploaded_file)
        if uploaded_file:
            try:
                image_path = os.path.abspath(os.path.join(root_dir, '..', 'images', uploaded_file.name))
                print(image_path)
                with open(image_path, 'wb+') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                # Call prediction with only image_path (assuming predict_single_image supports this)
                pred_result = predict_single_image(image_path=image_path)
                print(pred_result)

                # Format verdict from prediction result
                if 'label' in pred_result and 'confidence' in pred_result:
                    label = pred_result['label']
                    confidence = pred_result['confidence']
                    # Normalize class: if label starts with 'p' (positive), else negative
                    classification = 'pos' if label.lower().startswith('p') else 'neg'
                    verdict = f"Confidence: {confidence * 100:.2f}% "
                else:
                    class_index = pred_result.get('class_index', '?')
                    confidence = pred_result.get('confidence', 0)
                    # Adjust mapping as needed
                    classification = 'pos' if class_index == 1 else 'neg'
                    verdict = f"Confidence: {confidence * 100:.2f}%"

            except Exception as e:
                error = f"Error during prediction: {str(e)}"
        else:
            error = "Please upload an image file."

    return render(request, 'index.html', {
        'image_url': image_url,
        'classification': classification,
        'verdict': verdict,
        'error': error,
    })
