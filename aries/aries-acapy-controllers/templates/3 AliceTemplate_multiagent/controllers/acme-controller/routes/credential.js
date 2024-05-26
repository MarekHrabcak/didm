const express = require('express');
const router = express.Router();
const { check, validationResult } = require('express-validator');

const NavLinkService = require('../services/NavLinkService');
const navLinkService = new NavLinkService();
navLinkService.registerCustomLinks([]);

router.use(function (req, res, next) {
    navLinkService.clearLinkClasses();
    navLinkService.setNavLinkActive('/credentials');
    next();
});

router.get('/', async function(req, res, next) {
    const agentService = require('../services/AgentService');

    const connections = (await agentService.getConnections()).filter(c => c.state === 'active');
    const schemas = await agentService.getSchemas();
    const definitions = await agentService.getCredentialDefinitions();

    console.log({connections, schemas, definitions})

    navLinkService.setCustomNavLinkActive('/credentials');

    res.render('credential', {
        navLinks: navLinkService.getNavLinks(),
        customNavLinks: navLinkService.getCustomNavLinks(),
        connections, schemas, definitions
    });
});

router.post('/credential/send', [], async (req, res, next) => {
    const agentService = require('../services/AgentService');

    await agentService.sendCredential(req.body);

    res.status(200);
})

// router.get('/request', handleRequestSchemaGet);

// router.post('/request', [
//     check('connection_id')
//         .notEmpty()
//         .withMessage('Connection ID is required'),
//     check('credential_definition_id')
//         .notEmpty()
//         .withMessage('Credential Definition ID is required'),
// ], handleRequestProofPost, handleRequestSchemaGet);

// async function handleRequestSchemaGet(req, res, next) {
//     const agentService = require('../services/AgentService');
//     const schemas = await agentService.getSchemas();

//     if (req.errors) {
//         res.status(422);
//     }

//     navLinkService.setCustomNavLinkActive('/proofs/request');

//     res.render('request_proof', {
//         navLinks: navLinkService.getNavLinks(),
//         customNavLinks: navLinkService.getCustomNavLinks(),
//         connections: schemas,
//         errors: req.errors || null,
//         error_keys: (req.errors || []).map(error => error.param),
//         proof: {
//             proof: (req.errors && req.proof.proof_object) || JSON.stringify(proofJSON, null, 4),
//             connectionId: req.errors && req.proof.connection_id,
//             credentialDefinitionId: req.errors && req.proof.credential_definition_id,
//         }
//     });
// }

// async function handleRequestProofPost(req, res, next) {
//     const agentService = require('../services/AgentService');

//     const errors = validationResult(req);

//     if (!errors.isEmpty()) {
//         req.errors = errors.array();
//         req.proof = req.body;
//         return next();
//     }

//     await agentService.sendProofRequest(req.body.proof_object);
//     res.status(201).redirect('/proofs');
// }

module.exports = router;