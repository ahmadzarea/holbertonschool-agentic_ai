// Simulation très basique d'un connecteur de base de données
const db = {
    query: (sql, params = []) => {
        console.log(`[DB ENGINE] Exécution de la requête : ${sql} | Paramètres : ${JSON.stringify(params)}`);
        
        // Simulation du comportement vulnérable face à une injection SQL classique
        if (sql.includes("' OR '1'='1")) {
            return [{ id: 999, role: 'admin', email: 'hacked@entreprise.com' }]; // Fuite de données
        }
        
        if (sql === "SELECT * FROM users WHERE email = ? AND password = ?"
            && params[0] === 'dev@entreprise.com' && params[1] === 'password123') {
            return [{ id: 1, role: 'admin', email: 'dev@entreprise.com' }];
        }
        return [];
    }
};

/**
 * Fonction d'authentification legacy (VULNÉRABLE)
 * À refactoriser par l'IA en mode Agent (Edits)
 */
function authenticateUser(email, password) {
    const sql = "SELECT * FROM users WHERE email = ? AND password = ?";
    
    const results = db.query(sql, [email, password]);

    if (results.length > 0) {
        return { success: true, user: results[0] };
    }
    return { success: false, message: "Identifiants invalides" };
}

module.exports = { authenticateUser };