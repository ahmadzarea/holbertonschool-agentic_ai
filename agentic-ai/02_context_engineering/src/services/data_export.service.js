const userRepository = require('../repositories/user.repository');

class DataExportService {
    /**
     * Export all data held about a user
     * @param {string} email 
     * @returns {Object}
     */
    async exportUserData(email) {
        const user = userRepository.findByEmail(email);
        if (!user) {
            throw new Error("User not found in the system");
        }
        return {
            exportedAt: new Date().toISOString(),
            email,
            data: { ...user },
        };
    }
}

module.exports = new DataExportService();
