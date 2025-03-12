#!/usr/bin/env python3
import matplotlib.pyplot as plt
import re
import numpy as np
import sys

def extract_metrics(filename):
    """Extraire les métriques importantes des fichiers de résultats ab"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Extraire les requêtes par seconde
    rps_matches = re.findall(r'Requests per second:\s+([\d.]+)', content)
    rps = [float(x) for x in rps_matches]
    
    # Extraire le temps par requête
    tpr_matches = re.findall(r'Time per request:\s+([\d.]+)(?:.+)\[ms\] \(mean\)', content)
    tpr = [float(x) for x in tpr_matches]
    
    # Extraire le taux de transfert
    transfer_matches = re.findall(r'Transfer rate:\s+([\d.]+)', content)
    transfer = [float(x) for x in transfer_matches]
    
    return {
        'rps': rps,
        'tpr': tpr,
        'transfer': transfer
    }

def plot_comparison(lb_metrics, no_lb_metrics):
    """Générer des graphiques comparatifs"""
    # Configurer le style des graphiques
    plt.style.use('ggplot')
    
    # Créer une figure avec 3 sous-graphiques
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
    
    # Données pour les graphiques
    labels = ['Avec Load Balancing', 'Sans Load Balancing']
    rps_means = [np.mean(lb_metrics['rps']), np.mean(no_lb_metrics['rps'])]
    rps_std = [np.std(lb_metrics['rps']), np.std(no_lb_metrics['rps'])]
    
    tpr_means = [np.mean(lb_metrics['tpr']), np.mean(no_lb_metrics['tpr'])]
    tpr_std = [np.std(lb_metrics['tpr']), np.std(no_lb_metrics['tpr'])]
    
    transfer_means = [np.mean(lb_metrics['transfer']), np.mean(no_lb_metrics['transfer'])]
    transfer_std = [np.std(lb_metrics['transfer']), np.std(no_lb_metrics['transfer'])]
    
    # Positionnement des barres
    x = np.arange(len(labels))
    width = 0.35
    
    # Graphique 1: Requêtes par seconde
    bars1 = ax1.bar(x, rps_means, width, yerr=rps_std, capsize=5)
    ax1.set_title('Requêtes par seconde')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.bar_label(bars1, fmt='%.1f')
    
    # Graphique 2: Temps par requête
    bars2 = ax2.bar(x, tpr_means, width, yerr=tpr_std, capsize=5)
    ax2.set_title('Temps par requête (ms)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.bar_label(bars2, fmt='%.1f')
    
    # Graphique 3: Taux de transfert
    bars3 = ax3.bar(x, transfer_means, width, yerr=transfer_std, capsize=5)
    ax3.set_title('Taux de transfert (KB/s)')
    ax3.set_xticks(x)
    ax3.set_xticklabels(labels)
    ax3.bar_label(bars3, fmt='%.1f')
    
    # Ajuster la mise en page
    fig.tight_layout()
    
    # Sauvegarder le graphique
    plt.savefig('performance_comparison.png', dpi=300)
    print("Graphique sauvegardé sous 'performance_comparison.png'")
    
    # Afficher le graphique
    plt.show()

def main():
    try:
        # Charger les métriques
        lb_metrics = extract_metrics('results_with_lb.txt')
        no_lb_metrics = extract_metrics('results_without_lb.txt')
        
        # Générer les graphiques
        plot_comparison(lb_metrics, no_lb_metrics)
        
        # Afficher les statistiques
        print("\nStatistiques avec Load Balancing:")
        print(f"Requêtes par seconde: {np.mean(lb_metrics['rps']):.2f} ± {np.std(lb_metrics['rps']):.2f}")
        print(f"Temps par requête (ms): {np.mean(lb_metrics['tpr']):.2f} ± {np.std(lb_metrics['tpr']):.2f}")
        print(f"Taux de transfert (KB/s): {np.mean(lb_metrics['transfer']):.2f} ± {np.std(lb_metrics['transfer']):.2f}")
        
        print("\nStatistiques sans Load Balancing:")
        print(f"Requêtes par seconde: {np.mean(no_lb_metrics['rps']):.2f} ± {np.std(no_lb_metrics['rps']):.2f}")
        print(f"Temps par requête (ms): {np.mean(no_lb_metrics['tpr']):.2f} ± {np.std(no_lb_metrics['tpr']):.2f}")
        print(f"Taux de transfert (KB/s): {np.mean(no_lb_metrics['transfer']):.2f} ± {np.std(no_lb_metrics['transfer']):.2f}")
        
        # Calculer l'amélioration en pourcentage
        rps_improvement = (np.mean(lb_metrics['rps']) / np.mean(no_lb_metrics['rps']) - 1) * 100
        tpr_improvement = (np.mean(no_lb_metrics['tpr']) / np.mean(lb_metrics['tpr']) - 1) * 100
        transfer_improvement = (np.mean(lb_metrics['transfer']) / np.mean(no_lb_metrics['transfer']) - 1) * 100
        
        print("\nAméliorations avec Load Balancing:")
        print(f"Augmentation des requêtes par seconde: {rps_improvement:.2f}%")
        print(f"Réduction du temps par requête: {tpr_improvement:.2f}%")
        print(f"Augmentation du taux de transfert: {transfer_improvement:.2f}%")
        
    except FileNotFoundError as e:
        print(f"Erreur: {e}")
        print("Assurez-vous d'exécuter d'abord le script benchmark.sh pour générer les fichiers de résultats.")
        sys.exit(1)

if __name__ == "__main__":
    main()