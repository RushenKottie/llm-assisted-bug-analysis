from evaluation_metrics import calculate_metrics

print('''
      _________________________
      Raw comparison metrics
      _________________________
      ''')
agreement_raw = calculate_metrics("data/results/predicted_results.csv")

print('''
      ___________________________________________________________________
      Metrics after QA consilium and manual validation of model reasoning
      ___________________________________________________________________
      ''')
agreement_cons = calculate_metrics("data/results/qa_consilium.csv")

print(f"Change rate: {agreement_cons - agreement_raw:.2f}%")